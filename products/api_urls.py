from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ProductListAPIView

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')



app_name = 'products_api'

urlpatterns = [
    path('', ProductListAPIView.as_view(), name='api-product-list'),
    path('', include(router.urls)),
]
