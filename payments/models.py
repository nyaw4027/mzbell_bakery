from django.db import models

# Create your models here.
from django.db import models
from orders.models import Order
import uuid

class Payment(models.Model):
    PAYMENT_METHODS = [
        ('mtn_momo', 'MTN Mobile Money'),
        ('vodafone_cash', 'Vodafone Cash'),
        ('airteltigo_money', 'AirtelTigo Money'),
        ('card', 'Credit/Debit Card'),
        ('cash', 'Cash on Delivery'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)  # For mobile money
    reference = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Payment {self.id} - {self.method}"