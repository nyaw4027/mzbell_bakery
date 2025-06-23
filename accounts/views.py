from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import login, logout
from .serializers import UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer
import requests


class RegisterView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Create auth token
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'user': UserProfileSerializer(user).data,
            'token': token.key
        }, status=status.HTTP_201_CREATED)


class LoginView(generics.CreateAPIView):
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        # Get or create token
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'user': UserProfileSerializer(user).data,
            'token': token.key
        })


class LogoutView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        try:
            # Delete the user's token
            request.user.auth_token.delete()
        except:
            pass
        
        return Response({'message': 'Successfully logged out'})


class ProfileView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class UpdateProfileView(generics.UpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        # Handle location update
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        if latitude and longitude:
            try:
                from django.contrib.gis.geos import Point
                user.location = Point(float(longitude), float(latitude))
            except ImportError:
                # GIS not available, skip location update
                pass
        
        serializer.save()
        return Response(serializer.data)


def process_momo_payment(payment):
    """
    Process Mobile Money payment using MTN MoMo API
    This is a placeholder - you'll need to integrate with actual APIs
    """
    try:
        # Example MTN MoMo integration
        if payment.method == 'mtn_momo':
            # Make API call to MTN MoMo
            response = requests.post(
                'https://sandbox.momodeveloper.mtn.com/collection/v1_0/requesttopay',
                headers={
                    'Authorization': 'Bearer your-access-token',
                    'X-Reference-Id': payment.reference,
                    'X-Target-Environment': 'sandbox',
                    'Content-Type': 'application/json',
                },
                json={
                    'amount': str(payment.amount),
                    'currency': 'GHS',
                    'externalId': str(payment.id),
                    'payer': {
                        'partyIdType': 'MSISDN',
                        'partyId': payment.phone_number
                    },
                    'payerMessage': f'Payment for MzBell\'s Bakery Order {payment.order.id}',
                    'payeeNote': 'MzBell\'s Bakery Payment'
                }
            )
            
            if response.status_code == 202:
                payment.transaction_id = payment.reference
                return True
        
        return False
    except Exception as e:
        print(f"Payment processing error: {e}")
        return False
    
def signup_view(request):
    return render(request, 'accounts/signup.html')
