from django.urls import path
from . import views

app_name = 'frontend'

urlpatterns = [
    # Home and main pages
    path('', views.home, name='home'),
    path('products/', views.products, name='products'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('menu/', views.menu, name='menu'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),  # Changed from contact_view to contact
    path('services/', views.services, name='services'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('gallery/', views.gallery_view, name='gallery'),
    path('gallery/', views.GalleryView.as_view(), name='gallery'),
    
    # Shopping cart
    path('cart/', views.cart, name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('update-cart/<int:product_id>/', views.update_cart, name='update_cart'),
    path('remove-from-cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    
    # Checkout and orders
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/process/', views.process_checkout, name='process_checkout'),
    path('checkout/success/', views.checkout_success, name='checkout_success'),
    path('orders/', views.orders, name='orders'),
    path('order/<str:order_id>/', views.order_detail, name='order_detail'),
    path('order-confirmation/<str:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('track-order/<str:order_id>/', views.track_order, name='track_order'),
    
    # Special services
    path('custom-orders/', views.custom_order_form, name='custom_order_form'),
    path('catering/', views.catering, name='catering'),
    path('events/', views.events, name='events'),
    
    # Payment
    path('payment/momo/', views.initiate_momo_payment, name='initiate_momo_payment'),
    
    # AJAX endpoints
    path('api/cart-count/', views.get_cart_count, name='get_cart_count'),
    path('api/search-products/', views.search_products, name='search_products'),
]