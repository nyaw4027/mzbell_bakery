from django.urls import path
from .views import (
    DeliveryTrackingView,
    delivery_detail_view,
    update_delivery_location,
    update_delivery_location_api,
    DeliveryStatusView,
    MyDeliveriesView,
    track_delivery_view  # <-- This is the new map template view
)

app_name = 'delivery'

urlpatterns = [
    # API & logic views
    path('api/update-location/<uuid:delivery_id>/', update_delivery_location_api, name='update_location_api'),
    path('update-location/<uuid:delivery_id>/', update_delivery_location, name='update_location'),

    # View delivery tracking data (DRF-style API)
    path('status/<uuid:order_id>/', DeliveryStatusView.as_view(), name='delivery_status'),
    path('track-data/<uuid:order_id>/', DeliveryTrackingView.as_view(), name='delivery_tracking_data'),

    # View for delivery person to view their assigned orders
    path('my-deliveries/', MyDeliveriesView.as_view(), name='my_deliveries'),

    # 👇 NEW: Template-based tracking view for customer
    path('track/<uuid:order_id>/', track_delivery_view, name='track_delivery'),
    path('<int:delivery_id>/', delivery_detail_view, name='delivery_detail'),
]
