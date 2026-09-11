"""
Configuración principal de Django para el Sistema de Gestión Académica
"Del Colegio a Unisimón" — Universidad Simón Bolívar

Configuración compatible con:
- Desarrollo local con SQLite
- Producción en Railway con PostgreSQL
"""

import os
from pathlib import Path

from decouple import config
import dj_database_url


# ==============================================================================
# PATHS
# ==============================================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# ==============================================================================
# SECURITY
# ==============================================================================

SECRET_KEY = config(
    'SECRET_KEY',
    default='django-insecure-dev-key-change-in-production'
)

DEBUG = config(
    'DEBUG',
    default=True,
    cast=bool
)


# ==============================================================================
# ALLOWED HOSTS
# ==============================================================================

ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='localhost,127.0.0.1',
    cast=lambda v: [host.strip() for host in v.split(',') if host.strip()]
)


# Si Railway proporciona el dominio público mediante RAILWAY_PUBLIC_DOMAIN
railway_domain = os.environ.get('RAILWAY_PUBLIC_DOMAIN')

if railway_domain and railway_domain not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(railway_domain)


# ==============================================================================
# APPLICATIONS
# ==============================================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'widget_tweaks',

    # Local apps
    'apps.auth_app',
    'apps.dashboard',
    'apps.estudiantes',
    'apps.profesores',
    'apps.materias',
    'apps.espacios',
    'apps.asignaciones',
    'apps.asistencia',
    'apps.notas',
    'apps.reportes',
]


# ==============================================================================
# MIDDLEWARE
# ==============================================================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


ROOT_URLCONF = 'config.urls'


# ==============================================================================
# TEMPLATES
# ==============================================================================

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


WSGI_APPLICATION = 'config.wsgi.application'


# ==============================================================================
# DATABASE
# ==============================================================================
#
# LOCAL:
#   Si no existe DATABASE_URL → SQLite
#
# RAILWAY:
#   DATABASE_URL → PostgreSQL
#
# ==============================================================================

DATABASE_URL = os.environ.get('DATABASE_URL')


if DATABASE_URL:

    DATABASES = {
        'default': dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
            ssl_require=True,
        )
    }

else:

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# ==============================================================================
# AUTHENTICATION
# ==============================================================================

AUTH_USER_MODEL = 'auth_app.Usuario'

LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/auth/login/'


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME':
        'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.MinimumLengthValidator'
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.CommonPasswordValidator'
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.NumericPasswordValidator'
    },
]


# ==============================================================================
# INTERNATIONALIZATION
# ==============================================================================

LANGUAGE_CODE = 'es-co'

TIME_ZONE = 'America/Bogota'

USE_I18N = True

USE_TZ = True


# ==============================================================================
# STATIC FILES
# ==============================================================================

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / 'static'
]

STATIC_ROOT = BASE_DIR / 'staticfiles'

STORAGES = {
    'staticfiles': {
        'BACKEND':
        'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}


# ==============================================================================
# MEDIA FILES
# ==============================================================================

MEDIA_URL = '/media/'

MEDIA_ROOT = BASE_DIR / 'media'


# ==============================================================================
# DEFAULT PRIMARY KEY
# ==============================================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ==============================================================================
# SESSION CONFIGURATION
# ==============================================================================

SESSION_COOKIE_AGE = 3600

SESSION_COOKIE_HTTPONLY = True

SESSION_EXPIRE_AT_BROWSER_CLOSE = True


# ==============================================================================
# SECURITY - PRODUCTION
# ==============================================================================

if not DEBUG:

    SECURE_BROWSER_XSS_FILTER = True

    SECURE_CONTENT_TYPE_NOSNIFF = True

    SESSION_COOKIE_SECURE = True

    CSRF_COOKIE_SECURE = True

    SECURE_SSL_REDIRECT = True

    X_FRAME_OPTIONS = 'DENY'

    # Railway funciona detrás de un proxy HTTPS.
    SECURE_PROXY_SSL_HEADER = (
        'HTTP_X_FORWARDED_PROTO',
        'https'
    )


# ==============================================================================
# CSRF TRUSTED ORIGINS
# ==============================================================================

CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    default='',
    cast=lambda v: [
        origin.strip()
        for origin in v.split(',')
        if origin.strip()
    ]
)


# ==============================================================================
# LOGGING
# ==============================================================================

LOGGING = {
    'version': 1,

    'disable_existing_loggers': False,

    'formatters': {
        'verbose': {
            'format':
            '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },

    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },

    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },

        'apps': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
