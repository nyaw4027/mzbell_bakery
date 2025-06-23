from django.urls import path
from . import views

urlpatterns = [
    path('process/<int:order_id>/', views.process_payment, name='process_payment'),
    path('status/<int:payment_id>/', views.payment_status, name='payment_status'),
    path('webhooks/mtn-momo/', views.mtn_momo_webhook, name='mtn_momo_webhook'),
    path('webhooks/vodafone-cash/', views.vodafone_cash_webhook, name='vodafone_cash_webhook'),
    path('webhooks/airteltigo-money/', views.airteltigo_money_webhook, name='airteltigo_money_webhook'),
    path('delivery/location/<int:delivery_id>/', views.update_delivery_location, name='update_delivery_location'),
    path('delivery/tracking/<int:delivery_id>/', views.get_delivery_tracking, name='get_delivery_tracking'),
    # Legacy views
    path('momo/', views.initiate_momo_payment, name='initiate_momo_payment'),
    path('card/', views.initiate_card_payment, name='initiate_card_payment'),
]