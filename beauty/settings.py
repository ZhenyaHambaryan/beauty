import os, environ
env = environ.Env()
environ.Env.read_env()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = env("SECRET_KEY")

DEBUG = True

ALLOWED_HOSTS = ["*"]

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
    'django_filters',
    'simple_history',
    'django_crontab',
    
    'utils',
    'files',
    'userdetails',
    'timeline',
    'schedule',
    'notifications',
    'chat',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'simple_history.middleware.HistoryRequestMiddleware',
    'utils.middleware.ServerErrorExceptionHandler',
]

ROOT_URLCONF = 'beauty.urls'

STRIPE_API_KEY = "sk_live_SiGUm9ZRqYolWDgol2UCl4M100Ge0EW7Sj"

# STRIPE_API_KEY = "sk_test_I43UhLBhAMxZ9O3Hk0glw9hJ"

CRONJOBS = [
    ('*/2 * * * *', 'notifications.cron.scheduled_notification','>> /tmp/scheduled_notification.log 2>&1'),
    ('*/2 * * * *', 'notifications.cron.scheduled_push_notification','>> /tmp/scheduled_push_notification.log 2>&1'),
    ('*/2 * * * *', 'notifications.cron.scheduled_email','>> /tmp/scheduledemail.log 2>&1'),
    ('*/10 * * * *', 'schedule.cron.change_passed_status','>> /tmp/change_passed_status.log 2>&1'),
]

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

CORS_ORIGIN_ALLOW_ALL = True

WSGI_APPLICATION = 'beauty.wsgi.application'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': env("DATABASE_NAME"),
        'USER':env("DATABASE_USER"),
        'PASSWORD':env("DATABASE_PASSWORD"),
        'HOST':env("DATABASE_HOST"),
        'PORT':env("DATABASE_PORT"),
        'OPTIONS': {}
    }
}

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

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 10
}
# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

FIREBASE_PUSH_KEY = "AAAAN-cHc2I:APA91bHTwGyR9PGdhY3vghDP0fbo2oxSUUcc1V77VH-9hSjf46YDyfAP0-6NTSqwPYj_0gLPcBq5z5VhDIpasOoZgK_fQNCfdriYSeE3awVbJcNVlkPzABiE4MZNhR1Aa5epwYDCdb4b"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# EMAIL_BACKEND ="django.core.mail.backends.smtp.EmailBackend"
# EMAIL_HOST = "smtp.gmail.com"
# EMAIL_USE_TLS = True
# EMAIL_PORT = 587
# EMAIL_HOST_USER = "beatycoreemail@gmail.com"
# EMAIL_HOST_PASSWORD = "annaniks00"
# EMAIL_FROM = "beatycoreemail@gmail.com"

EMAIL_BACKEND ="django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "pro.turbo-smtp.com"
EMAIL_USE_SSL = True
EMAIL_PORT = 465
EMAIL_HOST_USER = "contact@beautycils.com"
EMAIL_HOST_PASSWORD = "123Killlosej@"
EMAIL_FROM = "contact@beautycils.com"
