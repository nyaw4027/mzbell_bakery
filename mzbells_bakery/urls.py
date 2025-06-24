from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('about/', TemplateView.as_view(template_name='about.html'), name='about'),

    # App routes with namespace
    path('accounts/', include(('accounts.urls', 'accounts'), namespace='accounts')),
    path('products/', include(('products.web_urls', 'frontend'), namespace='frontend')),

    path('api/products/', include(('products.api_urls', 'api_products'), namespace='api_products')),
    path('orders/', include(('orders.urls', 'orders'), namespace='orders')),
    path('users/', include(('users.urls', 'users'), namespace='users')),
    path('cart/', include(('cart.urls', 'cart'), namespace='cart')),
    path('', include(('frontend.urls', 'frontend'), namespace='frontend')),  # ✅ Include this
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
