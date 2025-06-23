from django.db import models
from django.contrib.auth import get_user_model
from orders.models import Order
import uuid
from django.utils import timezone

User = get_user_model()

class DeliveryZone(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    # Replace GIS fields with coordinate boundaries
    min_latitude = models.DecimalField(max_digits=10, decimal_places=8)
    max_latitude = models.DecimalField(max_digits=10, decimal_places=8)
    min_longitude = models.DecimalField(max_digits=11, decimal_places=8)
    max_longitude = models.DecimalField(max_digits=11, decimal_places=8)
    delivery_fee = models.DecimalField(max_digits=6, decimal_places=2)
    estimated_delivery_time = models.IntegerField(help_text="Estimated delivery time in minutes")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Delivery Zone'
        verbose_name_plural = 'Delivery Zones'

    def __str__(self):
        return f"{self.name} - ₵{self.delivery_fee}"

    def is_location_in_zone(self, latitude, longitude):
        """Check if given coordinates are within this delivery zone"""
        return (
            self.min_latitude <= latitude <= self.max_latitude and
            self.min_longitude <= longitude <= self.max_longitude
        )

class DeliveryPerson(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('busy', 'Busy'),
        ('offline', 'Offline'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    vehicle_type = models.CharField(max_length=50, help_text="e.g., Bicycle, Motorcycle, Car")
    license_number = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='offline')
    # Current location coordinates
    current_latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    current_longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    delivery_zones = models.ManyToManyField(DeliveryZone, related_name='delivery_persons')
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    total_deliveries = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Delivery Person'
        verbose_name_plural = 'Delivery Persons'

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.vehicle_type}"

    @property
    def current_location_display(self):
        """Returns formatted current location"""
        if self.current_latitude and self.current_longitude:
            return f"{self.current_latitude}, {self.current_longitude}"
        return "Location not set"

class Delivery(models.Model):
    STATUS_CHOICES = [
        ('assigned', 'Assigned'),
        ('picked_up', 'Picked Up'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='delivery')
    delivery_person = models.ForeignKey(DeliveryPerson, on_delete=models.SET_NULL, null=True, related_name='deliveries')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='assigned')
    pickup_time = models.DateTimeField(null=True, blank=True)
    delivery_time = models.DateTimeField(null=True, blank=True)
    estimated_arrival = models.DateTimeField(null=True, blank=True)
    delivery_notes = models.TextField(blank=True)
    delivery_proof = models.ImageField(upload_to='delivery_proof/', blank=True, null=True)
    customer_rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], null=True, blank=True)
    customer_feedback = models.TextField(blank=True)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Delivery'
        verbose_name_plural = 'Deliveries'

    def __str__(self):
        return f"Delivery for Order {str(self.order.id)[:8]}"

    @property
    def delivery_duration(self):
        """Calculate delivery duration if both times are set"""
        if self.pickup_time and self.delivery_time:
            return self.delivery_time - self.pickup_time
        return None

def mark_completed(self):
    self.is_completed = True
    self.completed_at = timezone.now()
    self.status = 'delivered'
    self.save()
    if self.delivery_person:
        self.delivery_person.status = 'available'
        self.delivery_person.save()


class DeliveryTracking(models.Model):
    delivery = models.ForeignKey(Delivery, on_delete=models.CASCADE, related_name='tracking_updates')
    # Location coordinates for tracking
    latitude = models.DecimalField(max_digits=10, decimal_places=8)
    longitude = models.DecimalField(max_digits=11, decimal_places=8)
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Delivery Tracking'
        verbose_name_plural = 'Delivery Tracking'

    def __str__(self):
        return f"Tracking for {self.delivery} at {self.timestamp}"

    @property
    def location_display(self):
        """Returns formatted location coordinates"""
        return f"{self.latitude}, {self.longitude}"
