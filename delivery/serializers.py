from rest_framework import serializers
from .models import Delivery, DeliveryTracking


class DeliveryTrackingSerializer(serializers.ModelSerializer):
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()
    
    class Meta:
        model = DeliveryTracking
        fields = ['id', 'latitude', 'longitude', 'timestamp', 'notes']
    
    def get_latitude(self, obj):
        return obj.location.y if obj.location else None
    
    def get_longitude(self, obj):
        return obj.location.x if obj.location else None


class DeliverySerializer(serializers.ModelSerializer):
    tracking_points = DeliveryTrackingSerializer(many=True, read_only=True)
    delivery_person_name = serializers.CharField(source='delivery_person.user.get_full_name', read_only=True)
    delivery_person_phone = serializers.CharField(source='delivery_person.user.phone_number', read_only=True)
    
    class Meta:
        model = Delivery
        fields = [
            'id', 'order', 'delivery_person_name', 'delivery_person_phone',
            'status', 'pickup_time', 'delivery_time', 'notes',
            'tracking_points', 'created_at', 'updated_at'
        ]