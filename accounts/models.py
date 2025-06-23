# Add this to the top of your accounts/models.py file

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# Conditional GIS import
try:
    if getattr(settings, 'USE_GIS', False):
        from django.contrib.gis.db import models as gis_models
        from django.contrib.gis.geos import Point
        GIS_AVAILABLE = True
    else:
        GIS_AVAILABLE = False
except ImportError:
    GIS_AVAILABLE = False

# If you had GIS fields, replace them with these conditional fields
def get_location_field():
    """Return appropriate location field based on GIS availability"""
    if GIS_AVAILABLE:
        return gis_models.PointField(null=True, blank=True)
    else:
        # Fallback to separate latitude/longitude fields
        return None

class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    
    # Conditional location field
    if GIS_AVAILABLE:
        location = gis_models.PointField(null=True, blank=True, srid=4326)
    else:
        # Fallback fields for location
        latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
        longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email