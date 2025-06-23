# frontend/urls.py (for serving web pages)
from django.urls import path
from . import views


app_name = 'frontend'


urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.products, name='products'),
    path('products/<int:product_id>/', views.product_detail, name='product-detail'),
    path('cart/', views.cart, name='cart'),
   
    path('orders/', views.orders, name='orders'),
    path('orders/<uuid:order_id>/', views.order_detail, name='order-detail'),
    path('track/<uuid:order_id>/', views.track_order, name='track-order'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('menu/', views.menu, name='menu'),
    path('custom-order/', views.custom_order_form, name='custom_order_form'),
    path('catering/', views.catering, name='catering'), 
    path('events/', views.events, name='events'), 
    path('services/', views.services, name='services'), 
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:product_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('order-confirmation/<str:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('ajax/cart-count/', views.get_cart_count, name='get_cart_count'),
    path('ajax/search/', views.search_products, name='search_products'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('custom-order/', views.custom_order_form, name='custom_order'),
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/process/', views.process_checkout, name='process_checkout'),
    path('checkout/success/', views.checkout_success, name='checkout_success'),  # optional
    path('checkout/initiate-momo/', views.initiate_momo_payment, name='initiate_momo_payment'),
    path('contact/', views.contact_view, name='contact'),
   



]