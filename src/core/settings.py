"""
Django settings for core project.
LifeBetter System - Arquitectura Limpia y Modular
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env si existe
load_dotenv()

# BASE_DIR apunta a la carpeta 'src/'
BASE_DIR = Path(__file__).resolve().parent.parent

# Configuración de Seguridad
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-_h1+#8^o99hh5lg60-lnff$t=x92+2%ocbli_-@$$)-w%abk4x')
DEBUG = int(os.getenv('DEBUG', '1')) == 1

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',')

# Definición de Aplicaciones Instaladas
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party
    'rest_framework',
    
    # Apps Locales del Dominio
    'apps.users',
    'apps.condo',
    'apps.expenses',
    'apps.payments',
    'apps.espacioscomunes',
]

# Custom User Model (RBAC)
AUTH_USER_MODEL = 'users.User'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

# Configuración del Motor de Plantillas HTML
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # CORRECCIÓN: Apuntamos explícitamente a la carpeta src/templates/
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

WSGI_APPLICATION = 'core.wsgi.application'

# Configuración de Base de Datos
DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': BASE_DIR / os.getenv('DB_NAME', 'db.sqlite3'),
    }
}

# Validadores de Contraseñas
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internacionalización y Zona Horaria Local (Chile)
LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True

# Archivos Estáticos
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static'
]

STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Credenciales Transbank Webpay Plus (Integración / Sandbox de pruebas)
TRANSBANK_COMMERCE_CODE = os.getenv('TRANSBANK_COMMERCE_CODE', '597055555532')
TRANSBANK_API_KEY = os.getenv('TRANSBANK_API_KEY', '579B532A7440BB07B079DADC822D872C')


# Configuración de Servidor de Correos (SMTP / SendGrid)
# En desarrollo (DEBUG=True) escribe los correos en la consola para testing rápido.
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.sendgrid.net')
    EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
    EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
    EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'apikey')
    EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')

DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'no-reply@lifebetter.cl')