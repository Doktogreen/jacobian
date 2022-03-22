import os
import cloudinary
# import django_heroku
from decouple import config
from corsheaders.defaults import default_headers
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'users.apps.UsersConfig',
    "wallet.apps.WalletConfig",
    'loan.apps.LoanConfig',
    'account',
    'dashboard',
    'transaction',
    'services',
    'cards',
    'settings',
    'django_filters',
    'debug_toolbar',
    'django_crontab'
]

CORS_ORIGIN_ALLOW_ALL = True

CORS_ALLOW_HEADERS = default_headers + (
    'Access-Control-Allow-Origin',
)
MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']

ROOT_URLCONF = 'simplefi.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'simplefi.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases


DATABASES = {
    'default': {
        'ENGINE': config('DATABASE_ENGINE'),
        'NAME': config('DATABASE_NAME'),
        'USER': config('DATABASE_USER'),
        'PASSWORD': config('DATABASE_PASSWORD'),
        'HOST': config('DATABASE_HOST'),
        'PORT': config('DATABASE_PORT')
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


CRONJOBS = [
    ("* 48 * * *", "simplefi.jobs.invoice_daily_reminder"),
    ("15 * * * *", "simplefi.jobs.checking_loan_status_on_crm")
]

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Africa/Lagos'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/


AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

# for heroku
# prod_db = dj_database_url.config(conn_max_age=500)
# DATABASES['default'].update(prod_db)

# for heroku
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/


PROJECT_ROOT = os.path.join(os.path.abspath(__file__))
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/staticfiles/'


# STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# STATIC_URL = '/static/'
# STATICFILES_DIRS = (
#     os.path.join(BASE_DIR, 'static'),
# )

# Extra lookup directories for collectstatic to find static files
# STATICFILES_DIRS = (
#     os.path.join(BASE_DIR, 'static'),
# )

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

#  Add configuration for static files storage using whitenoise
# STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'

CORS_ORIGIN_ALLOW_ALL = True
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT')
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = False


REST_FRAMEWORK = {

    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
}

INTERNAL_IPS = [
    '127.0.0.1', "localhost"
]

cloudinary.config(
    cloud_name=config("CLOUDINARY_CLOUD_NAME"),
    api_key=config("CLOUDINARY_API_KEY"),
    api_secret=config("CLOUDINARY_API_SECRET"),
    secure=True
)
