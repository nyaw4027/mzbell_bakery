# payments/views.py
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.conf import settings
from base64 import b64encode
import uuid
import requests
import logging

from .models import Payment
from .serializers import PaymentSerializer
from orders.models import Order
from delivery.models import Delivery, DeliveryTracking

# Conditional GIS imports
try:
    if getattr(settings, 'USE_GIS', False):
        from django.contrib.gis.geos import Point
        from django.contrib.gis.measure import D
        HAS_GIS = True
        print("✅ GIS functionality enabled")
    else:
        HAS_GIS = False
        Point = None
        print("ℹ️ GIS functionality disabled in settings")
except ImportError as e:
    HAS_GIS = False
    Point = None
    print(f"⚠️ GIS functionality not available: {e}")

# Set up logging
logger = logging.getLogger(__name__)


def create_location_point(latitude, longitude):
    """
    Create a location point with GIS if available, otherwise return dict
    """
    if HAS_GIS and latitude and longitude:
        try:
            return Point(float(longitude), float(latitude))
        except (ValueError, TypeError) as e:
            logger.error(f"Error creating Point: {e}")
            return {'latitude': float(latitude), 'longitude': float(longitude)}
    else:
        return {'latitude': float(latitude), 'longitude': float(longitude)}


def get_momo_access_token():
    """
    Get access token for MTN MoMo API
    """
    try:
        user_id = settings.MOMO_API_USER_ID
        api_key = settings.MOMO_API_KEY
        subscription_key = settings.MOMO_SUBSCRIPTION_KEY

        if not all([user_id, api_key, subscription_key]):
            raise Exception("Missing MoMo API credentials in settings")

        credentials = f"{user_id}:{api_key}"
        encoded_credentials = b64encode(credentials.encode()).decode()

        headers = {
            'Authorization': f'Basic {encoded_credentials}',
            'Ocp-Apim-Subscription-Key': subscription_key
        }

        response = requests.post(
            f"{settings.MOMO_API_URL}/collection/token/",
            headers=headers,
            timeout=30
        )

        if response.status_code == 200:
            return response.json().get('access_token')
        else:
            logger.error(f"Token generation failed: {response.status_code} - {response.text}")
            raise Exception(f"Token generation failed: {response.text}")
            
    except requests.RequestException as e:
        logger.error(f"Network error during token generation: {e}")
        raise Exception(f"Network error: {str(e)}")
    except Exception as e:
        logger.error(f"Error getting MoMo access token: {e}")
        raise


def initiate_momo_payment_request(order, phone_number):
    """
    Initiate MoMo payment request
    """
    try:
        reference_id = str(uuid.uuid4())
        access_token = get_momo_access_token()

        headers = {
            "Authorization": f"Bearer {access_token}",
            "X-Reference-Id": reference_id,
            "X-Target-Environment": settings.MOMO_TARGET_ENV,
            "Ocp-Apim-Subscription-Key": settings.MOMO_SUBSCRIPTION_KEY,
            "Content-Type": "application/json"
        }

        # Clean phone number (remove spaces, dashes, etc.)
        clean_phone = ''.join(filter(str.isdigit, phone_number))
        if clean_phone.startswith('0'):
            clean_phone = '233' + clean_phone[1:]  # Convert to international format
        elif not clean_phone.startswith('233'):
            clean_phone = '233' + clean_phone

        body = {
            "amount": str(order.total_amount),
            "currency": "GHS",
            "externalId": str(order.id),
            "payer": {
                "partyIdType": "MSISDN",
                "partyId": clean_phone
            },
            "payerMessage": "MzBell Bakery Order",
            "payeeNote": "Thank you for your purchase"
        }

        response = requests.post(
            f"{settings.MOMO_API_URL}/collection/v1_0/requesttopay",
            headers=headers,
            json=body,
            timeout=30
        )

        if response.status_code == 202:
            logger.info(f"MoMo payment initiated successfully: {reference_id}")
            return reference_id
        else:
            logger.error(f"Request to pay failed: {response.status_code} - {response.text}")
            raise Exception(f"Request to pay failed: {response.text}")
            
    except requests.RequestException as e:
        logger.error(f"Network error during payment request: {e}")
        raise Exception(f"Network error: {str(e)}")
    except Exception as e:
        logger.error(f"Error initiating MoMo payment: {e}")
        raise


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def process_payment(request, order_id):
    """
    Process payment for an order
    """
    try:
        order = get_object_or_404(Order, id=order_id, user=request.user)
        
        # Check if order is already paid
        if order.status in ['paid', 'completed']:
            return Response({
                'error': 'Order has already been paid'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        payment_method = request.data.get('payment_method')
        phone_number = request.data.get('phone_number', '')

        # Validate payment method
        valid_methods = ['mtn_momo', 'vodafone_cash', 'airteltigo_money', 'cash', 'card']
        if payment_method not in valid_methods:
            return Response({
                'error': f'Invalid payment method. Must be one of: {", ".join(valid_methods)}'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate phone number for mobile money
        if payment_method in ['mtn_momo', 'vodafone_cash', 'airteltigo_money']:
            if not phone_number:
                return Response({
                    'error': 'Phone number required for mobile money'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Basic phone number validation
            clean_phone = ''.join(filter(str.isdigit, phone_number))
            if len(clean_phone) < 10:
                return Response({
                    'error': 'Invalid phone number format'
                }, status=status.HTTP_400_BAD_REQUEST)

        # Create payment record
        payment = Payment.objects.create(
            order=order,
            method=payment_method,
            amount=order.total_amount,
            phone_number=phone_number,
            reference=str(uuid.uuid4())
        )

        # Process based on payment method
        if payment_method == 'cash':
            payment.status = 'pending'
            payment.save()
            order.status = 'confirmed'
            order.save()
            logger.info(f"Cash payment created for order {order.id}")
            
        elif payment_method == 'card':
            # For now, simulate card payment success
            # In production, integrate with actual card payment gateway
            payment.status = 'completed'
            payment.transaction_id = f"card_{uuid.uuid4()}"
            payment.save()
            order.status = 'confirmed'
            order.save()
            logger.info(f"Card payment processed for order {order.id}")
            
        else:  # Mobile money payments
            try:
                reference_id = initiate_momo_payment_request(order, phone_number)
                payment.reference = reference_id
                payment.status = 'pending'
                payment.save()
                order.status = 'processing'
                order.save()
                logger.info(f"Mobile money payment initiated for order {order.id}")
                
            except Exception as e:
                payment.status = 'failed'
                payment.save()
                logger.error(f"Mobile money payment failed for order {order.id}: {e}")
                return Response({
                    'error': f'Payment initiation failed: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        serializer = PaymentSerializer(payment)
        return Response({
            'payment': serializer.data,
            'order_status': order.status,
            'message': 'Payment processed successfully'
        })

    except Exception as e:
        logger.error(f"Error processing payment for order {order_id}: {e}")
        return Response({
            'error': 'An error occurred while processing payment'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([])
def mtn_momo_webhook(request):
    """
    Handle MTN MoMo webhook notifications
    """
    try:
        reference_id = request.headers.get('X-Reference-Id')
        if not reference_id:
            logger.warning("MTN MoMo webhook called without reference ID")
            return Response({'error': 'Missing reference ID'}, status=400)

        try:
            payment = Payment.objects.get(reference=reference_id)
        except Payment.DoesNotExist:
            logger.error(f"Payment not found for reference ID: {reference_id}")
            return Response({'error': 'Payment not found'}, status=404)

        # Get payment status from MoMo API
        access_token = get_momo_access_token()
        response = requests.get(
            f'{settings.MOMO_API_URL}/collection/v1_0/requesttopay/{reference_id}',
            headers={
                'Authorization': f'Bearer {access_token}',
                'X-Target-Environment': settings.MOMO_TARGET_ENV,
                'Ocp-Apim-Subscription-Key': settings.MOMO_SUBSCRIPTION_KEY,
            },
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'SUCCESSFUL':
                payment.status = 'completed'
                payment.transaction_id = data.get('financialTransactionId', '')
                payment.order.status = 'confirmed'
                payment.order.save()
                logger.info(f"Payment completed for reference: {reference_id}")
                
            elif data['status'] == 'FAILED':
                payment.status = 'failed'
                payment.order.status = 'cancelled'
                payment.order.save()
                logger.warning(f"Payment failed for reference: {reference_id}")
                
            payment.save()
        else:
            logger.error(f"Failed to get payment status: {response.status_code} - {response.text}")

        return Response({'status': 'success'})
        
    except requests.RequestException as e:
        logger.error(f"Network error in MoMo webhook: {e}")
        return Response({'error': 'Network error'}, status=500)
    except Exception as e:
        logger.error(f"Error in MTN MoMo webhook: {e}")
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([])
def vodafone_cash_webhook(request):
    """
    Handle Vodafone Cash webhook notifications
    TODO: Implement Vodafone Cash webhook logic
    """
    logger.info("Vodafone Cash webhook called")
    return Response({'status': 'success'})


@api_view(['POST'])
@permission_classes([])
def airteltigo_money_webhook(request):
    """
    Handle AirtelTigo Money webhook notifications
    TODO: Implement AirtelTigo Money webhook logic
    """
    logger.info("AirtelTigo Money webhook called")
    return Response({'status': 'success'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_delivery_location(request, delivery_id):
    """
    Update delivery person's location during delivery
    """
    try:
        delivery = get_object_or_404(Delivery, id=delivery_id)
        
        # Check authorization
        if delivery.delivery_person.user != request.user:
            return Response({
                'error': 'Unauthorized - you can only update your own deliveries'
            }, status=status.HTTP_403_FORBIDDEN)

        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        notes = request.data.get('notes', '')

        if not latitude or not longitude:
            return Response({
                'error': 'Both latitude and longitude are required'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            lat_float = float(latitude)
            lon_float = float(longitude)
            
            # Basic coordinate validation
            if not (-90 <= lat_float <= 90) or not (-180 <= lon_float <= 180):
                return Response({
                    'error': 'Invalid coordinates'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except (ValueError, TypeError):
            return Response({
                'error': 'Invalid coordinate format'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create location point
        location = create_location_point(lat_float, lon_float)

        # Create delivery tracking record
        if HAS_GIS:
            DeliveryTracking.objects.create(
                delivery=delivery,
                location=location,
                notes=notes
            )
            
            # Update delivery person's current location
            delivery.delivery_person.current_location = location
            delivery.delivery_person.save()
        else:
            # Handle without GIS - you might need to modify your models
            # to support non-GIS location storage
            DeliveryTracking.objects.create(
                delivery=delivery,
                # location=location,  # Comment out if your model requires Point
                notes=f"Location: {lat_float}, {lon_float}. {notes}"
            )

        logger.info(f"Location updated for delivery {delivery_id}: {lat_float}, {lon_float}")
        
        return Response({
            'status': 'Location updated successfully',
            'latitude': lat_float,
            'longitude': lon_float,
            'gis_enabled': HAS_GIS
        })
        
    except Exception as e:
        logger.error(f"Error updating delivery location: {e}")
        return Response({
            'error': 'An error occurred while updating location'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_delivery_tracking(request, delivery_id):
    """
    Get tracking information for a delivery
    """
    try:
        delivery = get_object_or_404(Delivery, id=delivery_id)
        
        # Check if user can view this delivery
        if delivery.order.user != request.user and delivery.delivery_person.user != request.user:
            return Response({
                'error': 'Unauthorized'
            }, status=status.HTTP_403_FORBIDDEN)

        tracking_records = DeliveryTracking.objects.filter(delivery=delivery).order_by('-timestamp')
        
        tracking_data = []
        for record in tracking_records:
            if HAS_GIS and hasattr(record, 'location') and record.location:
                tracking_data.append({
                    'timestamp': record.timestamp,
                    'latitude': record.location.y,
                    'longitude': record.location.x,
                    'notes': record.notes
                })
            else:
                # Handle non-GIS case - extract from notes or other fields
                tracking_data.append({
                    'timestamp': record.timestamp,
                    'notes': record.notes
                })

        return Response({
            'delivery_id': delivery_id,
            'tracking': tracking_data,
            'delivery_status': delivery.status,
            'gis_enabled': HAS_GIS
        })
        
    except Exception as e:
        logger.error(f"Error getting delivery tracking: {e}")
        return Response({
            'error': 'An error occurred while retrieving tracking information'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def initiate_momo_payment(request):
    """
    Legacy view for MoMo payment initiation (form-based)
    """
    if request.method == "POST":
        messages.success(request, "Payment successful! Redirecting to confirmation page.")
        return redirect('checkout_success')
    return redirect('checkout')


def initiate_card_payment(request):
    """
    Legacy view for card payment initiation (form-based)
    """
    if request.method == "POST":
        messages.success(request, "Payment successful! Your order is confirmed.")
        return redirect('checkout_success')
    return redirect('checkout')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_status(request, payment_id):
    """
    Get payment status
    """
    try:
        payment = get_object_or_404(Payment, id=payment_id, order__user=request.user)
        serializer = PaymentSerializer(payment)
        return Response(serializer.data)
    except Exception as e:
        logger.error(f"Error getting payment status: {e}")
        return Response({
            'error': 'Payment not found'
        }, status=status.HTTP_404_NOT_FOUND)