from django.contrib import admin
from .models import DeliveryZone, DeliveryPerson, Delivery, DeliveryTracking


@admin.register(DeliveryZone)
class DeliveryZoneAdmin(admin.ModelAdmin):
    list_display = ['name', 'delivery_fee', 'estimated_delivery_time', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']
    ordering = ['name']
    readonly_fields = ['created_at']


@admin.register(DeliveryPerson)
class DeliveryPersonAdmin(admin.ModelAdmin):
    list_display = ['user_full_name', 'vehicle_type', 'status', 'rating', 'total_deliveries', 'is_active']
    list_filter = ['status', 'vehicle_type', 'is_active']
    search_fields = ['user__username', 'user__email', 'phone_number']
    filter_horizontal = ['delivery_zones']
    readonly_fields = ['total_deliveries', 'rating', 'created_at']

    def user_full_name(self, obj):
        return obj.user.get_full_name()
    user_full_name.short_description = 'Delivery Person'


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = [
        'short_order_id', 'delivery_person', 'status',
        'estimated_arrival', 'pickup_time', 'delivery_time', 'is_completed'
    ]
    list_filter = ['status', 'is_completed']
    search_fields = ['order__id', 'delivery_person__user__username']
    readonly_fields = [
        'order', 'delivery_person', 'pickup_time', 'delivery_time',
        'estimated_arrival', 'created_at', 'updated_at', 'completed_at'
    ]
    date_hierarchy = 'created_at'

    def short_order_id(self, obj):
        return str(obj.order.id)[:8]
    short_order_id.short_description = 'Order ID'


@admin.register(DeliveryTracking)
class DeliveryTrackingAdmin(admin.ModelAdmin):
    list_display = ['delivery', 'location_display', 'timestamp']
    list_filter = ['timestamp']
    search_fields = ['delivery__id']
    readonly_fields = ['timestamp']

    def location_display(self, obj):
        return f"{obj.latitude}, {obj.longitude}"
    location_display.short_description = 'Coordinates'
