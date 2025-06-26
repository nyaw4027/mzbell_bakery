import os
from pathlib import Path
from decouple import config, Csv

# --- BASE DIRECTORY ---
BASE_DIR = Path(__file__).resolve().parent.parent


# --- SECURITY SETTINGS ---
SECRET_KEY = config('SECRET_KEY', default='your-secret-key')
DEBUG = config('DEBUG', default=False, cast=bool)  # Changed to False for production
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv(), default='127.0.0.1,localhost,*.herokuapp.com,*.railway.app,*.vercel.app,*.netlify.app,*.pythonanywhere.com')


# --- GIS / GDAL CONFIGURATION ---
USE_GIS = config('USE_GIS', default=False, cast=bool)  # Changed default to False

# Only configure GIS for local development (not in production)
if os.name == 'nt' and USE_GIS and DEBUG:
    # Extended GDAL paths for different versions
    gdal_paths = [
        'C:/OSGeo4W/bin/gdal304.dll',
        'C:/OSGeo4W64/bin/gdal304.dll',
        'C:/OSGeo4W/bin/gdal310.dll',
        'C:/OSGeo4W64/bin/gdal310.dll',
        'C:/OSGeo4W/bin/gdal309.dll',
        'C:/OSGeo4W64/bin/gdal309.dll',
        'C:/Program Files/GDAL/gdal304.dll',
        'C:/Program Files/GDAL/gdal310.dll',
        'C:/conda/Library/bin/gdal304.dll',
        'C:/conda/Library/bin/gdal310.dll',
        'C:/Miniconda3/Library/bin/gdal304.dll',
        'C:/Miniconda3/Library/bin/gdal310.dll',
        os.environ.get('GDAL_LIBRARY_PATH', '')
    ]
    
    geos_paths = [
        'C:/OSGeo4W/bin/geos_c.dll',
        'C:/OSGeo4W64/bin/geos_c.dll',
        'C:/Program Files/GDAL/geos_c.dll',
        'C:/conda/Library/bin/geos_c.dll',
        'C:/Miniconda3/Library/bin/geos_c.dll',
        os.environ.get('GEOS_LIBRARY_PATH', '')
    ]

    # Find existing GDAL and GEOS libraries
    GDAL_LIBRARY_PATH = next((p for p in gdal_paths if p and os.path.exists(p)), None)
    GEOS_LIBRARY_PATH = next((p for p in geos_paths if p and os.path.exists(p)), None)

    if GDAL_LIBRARY_PATH and GEOS_LIBRARY_PATH:
        print(f"✅ GDAL found at: {GDAL_LIBRARY_PATH}")
        print(f"✅ GEOS found at: {GEOS_LIBRARY_PATH}")
        
        # Set environment variables for GDAL/GEOS
        os.environ['GDAL_LIBRARY_PATH'] = GDAL_LIBRARY_PATH
        os.environ['GEOS_LIBRARY_PATH'] = GEOS_LIBRARY_PATH
        
        # Add GDAL data and projections paths
        gdal_dir = os.path.dirname(GDAL_LIBRARY_PATH)
        potential_data_paths = [
            os.path.join(gdal_dir, '..', 'share', 'gdal'),
            os.path.join(gdal_dir, '..', 'data'),
            'C:/OSGeo4W64/share/gdal',
            'C:/OSGeo4W/share/gdal',
        ]
        
        for data_path in potential_data_paths:
            if os.path.exists(data_path):
                os.environ['GDAL_DATA'] = data_path
                break
                
        potential_proj_paths = [
            os.path.join(gdal_dir, '..', 'share', 'proj'),
            'C:/OSGeo4W64/share/proj',
            'C:/OSGeo4W/share/proj',
        ]
        
        for proj_path in potential_proj_paths:
            if os.path.exists(proj_path):
                os.environ['PROJ_LIB'] = proj_path
                break
    else:
        USE_GIS = False
        print("⚠️ GIS support disabled — GDAL or GEOS not found on Windows.")


# --- APPLICATIONS ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    # Third-party
    'rest_framework',
    'corsheaders',
    'crispy_forms',
    'crispy_bootstrap5',

    # Local apps
    'accounts',
    'products',
    'orders',
    'payments',
    'delivery',
    'frontend',
    'users',
    'cart',
]

# Only add GIS if it's properly configured
if USE_GIS and DEBUG:  # Only enable GIS in development
    INSTALLED_APPS.insert(0, 'django.contrib.gis')


# --- MIDDLEWARE ---
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Add WhiteNoise middleware only if available (for production)
try:
    import whitenoise
    MIDDLEWARE.insert(2, 'whitenoise.middleware.WhiteNoiseMiddleware')
    # Static files compression for production
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
except ImportError:
    # WhiteNoise not installed - use default static files handling
    pass


# --- URLS AND WSGI ---
ROOT_URLCONF = 'mzbells_bakery.urls'
WSGI_APPLICATION = 'mzbells_bakery.wsgi.application'


# --- TEMPLATES ---
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# --- DATABASES ---
# Always use SQLite3 as the primary database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Optional: Override with PostgreSQL only if explicitly configured for production
if config('USE_POSTGRESQL', default=False, cast=bool) and config('DATABASE_URL', default=None):
    # Import dj_database_url only when needed
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.parse(config('DATABASE_URL'))
    }
elif config('USE_POSTGRESQL', default=False, cast=bool) and config('DB_NAME', default=None):
    # Use PostGIS if GIS is enabled and we have DB config
    if USE_GIS:
        DATABASES = {
            'default': {
                'ENGINE': 'django.contrib.gis.db.backends.postgis',
                'NAME': config('DB_NAME'),
                'USER': config('DB_USER'),
                'PASSWORD': config('DB_PASSWORD'),
                'HOST': config('DB_HOST', default='localhost'),
                'PORT': config('DB_PORT', default='5432'),
            }
        }
    else:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': config('DB_NAME'),
                'USER': config('DB_USER'),
                'PASSWORD': config('DB_PASSWORD'),
                'HOST': config('DB_HOST', default='localhost'),
                'PORT': config('DB_PORT', default='5432'),
            }
        }


# --- AUTHENTICATION ---
AUTH_USER_MODEL = 'accounts.User'
LOGIN_REDIRECT_URL = 'users:dashboard'
LOGOUT_REDIRECT_URL = 'users:login'  
LOGIN_URL = 'users:login'


# --- PASSWORD VALIDATION ---
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# --- INTERNATIONALIZATION ---
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Accra'
USE_I18N = True
USE_TZ = True


# --- STATIC AND MEDIA FILES ---
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# --- DEFAULT FIELD TYPE ---
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# --- REST FRAMEWORK ---
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
}


# --- CORS ---
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://mzbellsbakery.com",
    "http://127.0.0.1:8000",
    "http://localhost:8000",
]

# Allow all origins in development
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True


# --- EMAIL CONFIGURATION ---
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='your_email@gmail.com')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='your-password')
DEFAULT_FROM_EMAIL = 'MzBell Bakery <no-reply@mzbellsbakery.com>'


# --- LOGGING ---
LOGGING_DIR = BASE_DIR / 'logs'
os.makedirs(LOGGING_DIR, exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} - {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': LOGGING_DIR / 'delivery.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'delivery': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}


# --- MOBILE MONEY / MOMO API ---
MOMO_API_URL = config('MOMO_API_URL', default='https://sandbox.momodeveloper.mtn.com')
MOMO_API_USER_ID = config('MOMO_API_USER_ID', default='')
MOMO_API_KEY = config('MOMO_API_KEY', default='')
MOMO_ACCESS_TOKEN = config('MOMO_ACCESS_TOKEN', default='')
MOMO_SUBSCRIPTION_KEY = config('MOMO_SUBSCRIPTION_KEY', default='')
MOMO_TARGET_ENV = config('MOMO_TARGET_ENV', default='sandbox')
MOMO_CALLBACK_HOST = config('MOMO_CALLBACK_HOST', default='https://webhook.site/your-id')


# --- GOOGLE MAPS ---
GOOGLE_MAPS_API_KEY = config('GOOGLE_MAPS_API_KEY', default='')


# --- CRISPY FORMS ---
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"


# --- SECURITY SETTINGS FOR PRODUCTION ---
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_REDIRECT_EXEMPT = []
    SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=False, cast=bool)
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    USE_TZ = True
    
    # Session security
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True


# --- GIS SETTINGS (only if GIS is enabled) ---
if USE_GIS:
    # Default map widget settings
    DEFAULT_SRID = 4326  # WGS84
    
    # Optional: Configure map widgets
    LEAFLET_CONFIG = {
        'DEFAULT_CENTER': (5.6037, -0.1870),  # Accra, Ghana coordinates
        'DEFAULT_ZOOM': 12,
        'MIN_ZOOM': 3,
        'MAX_ZOOM': 18,
    }