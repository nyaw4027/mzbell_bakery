
# orders/serializers.py
from rest_framework import serializers
from .models import Order, OrderItem
from products.serializers import ProductSerializer

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_image = serializers.ImageField(source='product.image', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'product_image', 
                 'quantity', 'price', 'special_requests', 'subtotal']
        read_only_fields = ['subtotal']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'user', 'user_name', 'status', 'total_amount',
            'delivery_address', 'phone_number', 'special_instructions',
            'delivery_fee', 'estimated_delivery_time', 'items',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'total_amount']

class CreateOrderSerializer(serializers.Serializer):
    items = serializers.ListField(child=serializers.DictField())
    delivery_address = serializers.CharField()
    delivery_latitude = serializers.FloatField()
    delivery_longitude = serializers.FloatField()
    phone_number = serializers.CharField()
    special_instructions = serializers.CharField(required=False, allow_blank=True)


          
    def validate_status(self, value):
        valid_statuses = ['pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled']
        if value not in valid_statuses:
            raise serializers.ValidationError(f"Invalid status. Must be one of: {valid_statuses}")
        return value
    

# Add these to your existing serializers.py file

class OrderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating orders with validation"""
    class Meta:
        model = Order
        fields = ['items', 'delivery_address', 'notes']  # Adjust fields as needed
        
    def validate(self, data):
        # Add custom validation logic here
        return data

class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    """Serializer specifically for updating order status"""
    class Meta:
        model = Order
        fields = ['status']
        
    def validate_status(self, value):
        valid_statuses = ['pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled']
        if value not in valid_statuses:
            raise serializers.ValidationError(f"Invalid status. Must be one of: {valid_statuses}")
        return value


