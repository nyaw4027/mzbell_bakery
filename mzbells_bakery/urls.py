from django.contrib import admin
from django.urls import path, include
from products import views as product_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', product_views.home, name='home'),

    # Admin and auth
    path('admin/', admin.site.urls),
    path('accounts/', include(('django.contrib.auth.urls', 'django.contrib.auth'), namespace='registration')),

    # API routes
    path('api/products/', include(('products.api_urls', 'products_api'), namespace='products_api')),
    path('api/orders/', include('orders.urls')),
    path('api/payments/', include('payments.urls')),
    path('api/delivery/', include('delivery.urls')),
    path('cart/', include(('cart.urls', 'cart'), namespace='cart')),

    # Web views
    path('products/', include(('products.web_urls', 'products'), namespace='products')),
    path('users/', include(('users.urls', 'users'), namespace='users')),

    path('payments/', include('payments.urls')),
    path('', include('frontend.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
