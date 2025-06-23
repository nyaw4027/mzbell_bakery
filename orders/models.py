from django.db import models
from django.conf import settings
from django.utils import timezone
from products.models import Product
import uuid

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready for Pickup/Delivery'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    order_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    delivery_address = models.TextField(blank=True, null=True)
    delivery_phone = models.CharField(max_length=20, blank=True, null=True)
    delivery_notes = models.TextField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)   # ← Added for delivery mapping
    longitude = models.FloatField(blank=True, null=True)  # ← Added for delivery mapping
    is_paid = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    tx_ref = models.CharField(max_length=100, blank=True, null=True)  # Flutterwave reference

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.order_number} - {self.user.username if self.user else 'Guest'}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

    def get_total_price(self):
        return self.quantity * self.price


class CustomOrder(models.Model):
    PRODUCT_TYPES = [
        ('birthday_cake', 'Birthday Cake'),
        ('wedding_cake', 'Wedding Cake'),
        ('cupcakes', 'Cupcakes'),
    ]

    BUDGET_OPTIONS = [
        ('under_50', 'Under GHS 50'),
        ('50_to_100', 'GHS 50 - GHS 100'),
        ('over_100', 'Over GHS 100'),
    ]

    DELIVERY_CHOICES = [
        ('pickup', 'Pickup'),
        ('delivery', 'Delivery'),
    ]

    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    event_date = models.DateField()
    product_type = models.CharField(max_length=50, choices=PRODUCT_TYPES)
    servings = models.PositiveIntegerField()
    flavor = models.CharField(max_length=100)
    budget = models.CharField(max_length=20, choices=BUDGET_OPTIONS)
    requirements = models.TextField(blank=True)  # Store comma-separated
    design_description = models.TextField(blank=True)
    additional_notes = models.TextField(blank=True)
    delivery_option = models.CharField(max_length=20, choices=DELIVERY_CHOICES)
    delivery_address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Custom Order - {self.full_name} ({self.event_date})"
