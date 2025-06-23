from django.db.models.signals import post_save
from django.dispatch import receiver
from orders.models import Order
from .utils import assign_delivery_person_to_order

@receiver(post_save, sender=Order)
def auto_assign_delivery(sender, instance, created, **kwargs):
    if created and instance.status in ['confirmed', 'processing']:  # Adjust based on your logic
        assign_delivery_person_to_order(instance)
