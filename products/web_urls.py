from django.urls import path
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

app_name = 'products'

urlpatterns = [
    path('all/', product_list_view, name='product_list'),
    path('products/<slug:slug>/', product_detail, name='product_detail'),  # Changed to slug
    path('featured/', featured_products, name='featured_products'),
    path('cart/', view_cart, name='cart'),
    path('add-to-cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('custom-order/', custom_order, name='custom_order_form'),
    path('menu/', menu, name='menu'),
    path('categories/', category_list_view, name='category_list'),
    path('categories/<int:category_id>/', category_product_list, name='products_by_category'),
]
