from django.urls import path

from accounts.views import LogoutView
from . import views


app_name = "orders"



urlpatterns = [
    # List all orders and create new orders
    path('', views.OrderListCreateView.as_view(), name='order-list-create'),
    
    # Get specific order details
    path('<int:id>/', views.OrderDetailView.as_view(), name='order-detail'),
    
    # Update order status
    path('<int:id>/status/', views.OrderStatusUpdateView.as_view(), name='order-status-update'),
    
    # Cancel order
    path('<int:id>/cancel/', views.OrderCancelView.as_view(), name='order-cancel'),
    
    # User order statistics
    path('stats/', views.UserOrderStatsView.as_view(), name='order-stats'),

    path('checkout/', views.checkout_view, name='checkout'),
    path('confirm/', views.confirm_order, name='confirm_order'),
    path('my-orders/', views.order_list, name='order_list'),
    path('custom-order/', views.custom_order_view, name='custom_order'),
   
    path('confirmation/<str:order_number>/', views.order_confirmation, name='order_confirmation'),
    

   

]