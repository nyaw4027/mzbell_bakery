from django.urls import path
from django.views.generic import TemplateView
from .views import (
    product_list_view,
    ProductDetailView,
    product_detail,
    featured_products,
    view_cart,
    add_to_cart,
    custom_order,
    menu,
    category_list_view,
    category_product_list
)

app_name = 'frontend'
urlpatterns = [
    path('all/', product_list_view, name='product_list'),
    path('products/<slug:slug>/', product_detail, name='product_detail'),
    path('featured/', featured_products, name='featured_products'),
    path('cart/', view_cart, name='cart'),
    path('add-to-cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('custom-order/', custom_order, name='custom_order_form'),
    path('menu/', menu, name='menu'),
    path('categories/', category_list_view, name='category_list'),
    path('categories/<int:category_id>/', category_product_list, name='products_by_category'),

    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('contact/', TemplateView.as_view(template_name='frontend/contact.html'), name='contact'),
    path('about/', TemplateView.as_view(template_name='frontend/about.html'), name='about'),
    path('catering/', TemplateView.as_view(template_name='frontend/catering.html'), name='catering'),
    path('terms/', TemplateView.as_view(template_name='frontend/terms.html'), name='terms'),
    path('privacy/', TemplateView.as_view(template_name='frontend/privacy.html'), name='privacy'),
    path('faq/', TemplateView.as_view(template_name='frontend/faq.html'), name='faq'),
    path('blog/', TemplateView.as_view(template_name='frontend/blog.html'), name='blog'),
    path('events/', TemplateView.as_view(template_name='frontend/events.html'), name='events'),
    path('services/', TemplateView.as_view(template_name='frontend/services.html'), name='services'),
]
