# delivery/views.py
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, render, redirect
from .models import Delivery
from .serializers import DeliverySerializer
from orders.models import Order
from .forms import DeliveryFeedbackForm




from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view

from rest_framework import status
from rest_framework.views import APIView
import json
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib import messages






class DeliveryTrackingView(generics.RetrieveAPIView):
    serializer_class = DeliverySerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        order_id = self.kwargs['order_id']
        order = get_object_or_404(Order, id=order_id, user=self.request.user)
        return get_object_or_404(Delivery, order=order)
    
    
@csrf_exempt
@require_http_methods(["POST", "PUT"])
def update_delivery_location(request, delivery_id):
    """
    Update delivery location
    """
    try:
        delivery = get_object_or_404(Delivery, id=delivery_id)
        
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST
        
        # Update location fields
        if 'latitude' in data:
            delivery.current_latitude = data['latitude']
        if 'longitude' in data:
            delivery.current_longitude = data['longitude']
        if 'address' in data:
            delivery.current_address = data['address']
        if 'status' in data:
            delivery.status = data['status']
            
        delivery.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Delivery location updated successfully',
            'delivery_id': delivery.id,
            'status': delivery.status
        })
        
    except Delivery.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Delivery not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

# Alternative: REST Framework version
@api_view(['POST', 'PUT'])
def update_delivery_location_api(request, delivery_id):
    """
    REST API version to update delivery location
    """
    try:
        delivery = get_object_or_404(Delivery, id=delivery_id)
        
        # Update with partial data
        serializer = DeliverySerializer(delivery, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Delivery location updated successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Delivery.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Delivery not found'
        }, status=status.HTTP_404_NOT_FOUND)


# View: Get status for a specific delivery
class DeliveryStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        delivery = get_object_or_404(Delivery, order__id=order_id, order__user=request.user)
        return Response({
            'status': delivery.status,
            'estimated_arrival': delivery.estimated_arrival,
            'delivery_person': delivery.delivery_person.user.get_full_name() if delivery.delivery_person else "Unassigned",
        })


# View: Rider's list of deliveries
class MyDeliveriesView(generics.ListAPIView):
    serializer_class = DeliverySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Delivery.objects.filter(delivery_person__user=self.request.user)


@login_required
def track_delivery_view(request, order_id):
    from .models import Delivery
    from orders.models import Order

    order = get_object_or_404(Order, id=order_id, user=request.user)
    delivery = get_object_or_404(Delivery, order=order)

    return render(request, 'delivery/track_delivery.html', {
        'delivery': delivery
    })



@login_required
def delivery_detail_view(request, delivery_id):
    delivery = get_object_or_404(Delivery, id=delivery_id, delivery_person__user=request.user)

    if request.method == 'POST':
        if delivery.status != 'delivered':
            delivery.status = 'delivered'
            delivery.save()
            messages.success(request, f"Order {delivery.order.order_number} marked as delivered.")
            return redirect('delivery_detail', delivery_id=delivery.id)

    order = delivery.order
    return render(request, 'delivery/delivery_detail.html', {
        'delivery': delivery,
        'order': order,
        'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY,
    })



def delivery_feedback(request, delivery_id):
    delivery = get_object_or_404(Delivery, id=delivery_id, is_completed=True)

    if request.method == 'POST':
        form = DeliveryFeedbackForm(request.POST, instance=delivery)
        if form.is_valid():
            form.save()
            messages.success(request, "Thanks for rating your delivery!")
            return redirect('delivery_feedback', delivery_id=delivery.id)
    else:
        form = DeliveryFeedbackForm(instance=delivery)

    return render(request, 'delivery/feedback.html', {
        'form': form,
        'delivery': delivery
    })

