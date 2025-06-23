from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, PermissionDenied
from django.shortcuts import get_object_or_404, render, redirect
from django.db import transaction
from django.utils import timezone
from django.conf import settings
from django.contrib import messages
from .models import Order, OrderItem, Product
from .serializers import OrderSerializer
from django.views.generic import ListView
from rest_framework.views import APIView
from django.contrib.auth.decorators import login_required

from cart.cart import Cart  # Add this import for the Cart class


class OrderListCreateView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Order.objects.filter(user=self.request.user)
        
        # Add filtering options
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
            
        # Add ordering
        ordering = self.request.query_params.get('ordering', '-created_at')
        if ordering:
            queryset = queryset.order_by(ordering)
            
        return queryset.select_related('user').prefetch_related('items__product')
    
    def get_serializer_class(self):
        # Use the same serializer for both GET and POST for now
        return OrderSerializer
    
    @transaction.atomic
    def perform_create(self, serializer):
        # Validate that user has sufficient permissions/balance if needed
        order = serializer.save(user=self.request.user)
        
        # You can add additional logic here like:
        # - Inventory checks
        # - Payment processing
        # - Email notifications
        
        return order
    
    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except ValidationError as e:
            return Response(
                {'error': 'Validation failed', 'details': e.detail},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': 'Order creation failed', 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).select_related('user').prefetch_related('items__product')
    
    def get_object(self):
        """
        Override to provide better error handling
        """
        queryset = self.get_queryset()
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        
        try:
            obj = get_object_or_404(queryset, **filter_kwargs)
        except Exception:
            return Response(
                {'error': 'Order not found or access denied'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        self.check_object_permissions(self.request, obj)
        return obj


class OrderStatusUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    
    # Define allowed status transitions
    ALLOWED_TRANSITIONS = {
        'pending': ['confirmed', 'cancelled'],
        'confirmed': ['processing', 'cancelled'],
        'processing': ['shipped', 'cancelled'],
        'shipped': ['delivered'],
        'delivered': [],  # Final state
        'cancelled': []   # Final state
    }
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        # Use OrderSerializer for status updates
        return OrderSerializer
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        new_status = request.data.get('status')
        
        # Validate status transition
        if not self.is_valid_status_transition(instance.status, new_status):
            return Response(
                {
                    'error': f'Cannot change status from {instance.status} to {new_status}',
                    'allowed_transitions': self.ALLOWED_TRANSITIONS.get(instance.status, [])
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Additional business logic based on status
        if new_status == 'cancelled':
            self.handle_cancellation(instance)
        elif new_status == 'delivered':
            instance.delivered_at = timezone.now()
        
        return super().update(request, *args, **kwargs)
    
    def is_valid_status_transition(self, current_status, new_status):
        """Check if the status transition is allowed"""
        allowed_statuses = self.ALLOWED_TRANSITIONS.get(current_status, [])
        return new_status in allowed_statuses
    
    def handle_cancellation(self, order):
        """Handle order cancellation logic"""
        # Add logic for:
        # - Refund processing
        # - Inventory restoration
        # - Notification sending
        pass
    
    def perform_update(self, serializer):
        serializer.save(updated_at=timezone.now())


class OrderCancelView(generics.UpdateAPIView):
    """Dedicated view for order cancellation"""
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
    
    @transaction.atomic
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Check if order can be cancelled
        if instance.status not in ['pending', 'confirmed']:
            return Response(
                {'error': f'Cannot cancel order with status: {instance.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Perform cancellation
        instance.status = 'cancelled'
        instance.cancelled_at = timezone.now()
        instance.save()
        
        # Add cancellation reason if provided
        cancellation_reason = request.data.get('reason', 'Cancelled by user')
        
        return Response(
            {
                'message': 'Order cancelled successfully',
                'order_id': instance.id,
                'status': instance.status,
                'cancelled_at': instance.cancelled_at,
                'reason': cancellation_reason
            },
            status=status.HTTP_200_OK
        )


class UserOrderStatsView(generics.GenericAPIView):
    """View to get user's order statistics"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user_orders = Order.objects.filter(user=request.user)
        
        stats = {
            'total_orders': user_orders.count(),
            'pending_orders': user_orders.filter(status='pending').count(),
            'completed_orders': user_orders.filter(status='delivered').count(),
            'cancelled_orders': user_orders.filter(status='cancelled').count(),
            'total_spent': sum(order.total_amount for order in user_orders if order.status == 'delivered'),
            'recent_orders': OrderSerializer(
                user_orders.order_by('-created_at')[:5], 
                many=True
            ).data
        }
        
        return Response(stats, status=status.HTTP_200_OK)
    

class OrderListView(APIView):
    """
    API View to handle listing orders and creating new orders
    """
    def get(self, request):
        """Get all orders"""
        orders = Order.objects.all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        """Create a new order"""
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Alternative: If you prefer Django's generic ListView
class OrderListViewGeneric(ListView):
    """
    Generic ListView for orders (if you want to render HTML templates)
    """
    model = Order


@login_required

def checkout_view(request):
    cart = request.session.get('cart', {})
    product_ids = cart.keys()
    products = Product.objects.filter(id__in=product_ids)
    cart_items = []

    for product in products:
        quantity = cart[str(product.id)]
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'total_price': quantity * product.price
        })

    total = sum(item['total_price'] for item in cart_items)

    return render(request, 'orders/checkout.html', {
        'cart_items': cart_items,
        'total': total
    })

def confirm_order(request):
    return render(request, 'orders/confirm_order.html')

@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/order_list.html', {'orders': orders})

def custom_order_view(request):
    return render(request, 'orders/custom_order.html')


def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {
        'order': order,
        'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY,
    })


def order_confirmation(request, order_number):
    order = Order.objects.filter(order_number=order_number, user=request.user).first()
    if not order:
        messages.error(request, "Order not found.")
        return redirect('cart:view_cart')

    return render(request, 'orders/order_confirmation.html', {'order': order})
def custom_order_view(request):
    if request.method == 'POST':
        # Handle custom order form submission
        # You can create a custom order model and save the data here
        messages.success(request, "Your custom order request has been submitted!")
        return redirect('orders:order_list')

    return render(request, 'orders/custom_order.html', {'page_title': 'Custom Order'})

