from django import forms
from .models import Delivery, DeliveryPerson

class DeliveryFeedbackForm(forms.ModelForm):
    class Meta:
        model = Delivery
        fields = ['customer_rating', 'customer_feedback']
        widgets = {
            'customer_rating': forms.NumberInput(attrs={'min': 1, 'max': 5, 'class': 'form-input'}),
            'customer_feedback': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 4}),
        }
        labels = {
            'customer_rating': 'Rate this delivery (1–5)',
            'customer_feedback': 'Leave a comment (optional)',
        }

class DeliveryPersonForm(forms.ModelForm):
    class Meta:
        model = DeliveryPerson
        fields = [
            'phone_number',
            'vehicle_type',
            'license_number',
            'status',
            'current_latitude',
            'current_longitude',
            'delivery_zones',
            'rating',
            'total_deliveries',
            'is_active'
        ]
