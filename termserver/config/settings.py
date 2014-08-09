"""Terminology API server project settings"""
# -coding=utf-8
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SECRET_KEY = '36o32ca(s_*hzwh5*8snp($fajwwl&j%d08^xcnes4j-0rx$#3'
DEBUG = True
TEMPLATE_DEBUG = DEBUG
ALLOWED_HOSTS = ['.slade360.co.ke', '.localhost']
INSTALLED_APPS = (
    # Built in apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party apps
    'django_extensions',
    'rest_framework',
    'rest_framework_swagger',
    'rest_framework.authtoken',
    'debug_toolbar',
    'elasticutils.contrib.django',
    # Our apps
    'core',
    'refset',
    'search',
    'authoring',
    'expression_repository',
    'administration',
    'api',
)
MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'elasticutils.contrib.django.ESExceptionMiddleware',
)
ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'termserver',
        'USER': 'termserver',
        'PASSWORD': 'termserver',
        'HOST': '127.0.0.1',
        'PORT': '5432',
        'CONN_MAX_AGE': 300
    }
}
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_L10N = True
USE_TZ = True
STATIC_URL = '/static/'

# Task queue settings
BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
BROKER_TRANSPORT_OPTIONS = {
    'visibility_timeout': 120,  # Aggressive timeout, just 2 minutes
    'fanout_prefix': True,
    'fanout_patterns': True
}

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_MODEL_SERIALIZER_CLASS': 'rest_framework.serializers.HyperlinkedModelSerializer',
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissions'
    ],
    'PAGINATE_BY': 25,
    'PAGINATE_BY_PARAM': 'page_size',
    'MAX_PAGINATE_BY': 100,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_FILTER_BACKENDS': ['rest_framework.filters.DjangoFilterBackend',],
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    'TEST_REQUEST_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DATETIME_FORMAT': 'iso-8601',
    'DATETIME_INPUT_FORMATS': ['iso-8601'],
    'DATE_FORMAT': 'iso-8601',
    'DATE_INPUT_FORMATS': ['iso-8601']
}

# API Documentation
SWAGGER_SETTINGS = {
    "exclude_namespaces": [], # List URL namespaces to ignore
    "api_version": '1.0',
    "api_path": "/api/",
    "enabled_methods": [
        'get',
        'post',
        'put',
        'delete'
    ],
    "api_key": '',
    "is_authenticated": True,
    "is_superuser": False,
}

# Test optimizations
# Use nose
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = [
    "--with-coverage",
    "--cover-branches",
    "--cover-html",
    "--cover-html-dir=coverage_html_reports",
    "--cover-erase",
    "--cover-package=core,refset,search,authoring,administration,api",
    "--cover-min-percentage=100",
    "--with-xunit",
    "--with-fixture-bundling"]

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)

CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
CELERY_ALWAYS_EAGER = True
BROKER_BACKEND = 'memory'

# ElasticUtils configuration
ES_DISABLED = False
ES_URLS = ['http://localhost:9200']
ES_INDEXES = {'default': 'concept-index'}
ES_TIMEOUT = 5  # Number of seconds before timing out when creating a connection to ElasticSearch

# Logging
if DEBUG:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,  # Keep the existing Django loggers
        'formatters': {
            'verbose': {
                'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
            },
            'simple': {
                'format': '%(levelname)s %(message)s'
            },
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'simple'
            },
            'mail_admins': {
                'level': 'ERROR',
                'class': 'django.utils.log.AdminEmailHandler',
            }
        },
        'loggers': {
            # The libraries involved in search indexing
            'elasticsearch.trace': {
                'handlers': ['console'],
                'level': 'ERROR'
            },
            'elasticsearch': {
                'handlers': ['console'],
                'level': 'ERROR'
            },
            'urllib3': {
                'handlers': ['console'],
                'level': 'ERROR'
            },
            # Our apps
            'search': {
                'handlers': ['console'],
                'level': 'DEBUG'
            },
            'core': {
                'handlers': ['console'],
                'level': 'DEBUG'
            },
            'refset': {
                'handlers': ['console'],
                'level': 'DEBUG'
            },
            'administration': {
                'handlers': ['console'],
                'level': 'DEBUG'
            },
            'api': {
                'handlers': ['console'],
                'level': 'DEBUG'
            },
            'authoring': {
                'handlers': ['console'],
                'level': 'DEBUG'
            },
            'expression_repository': {
                'handlers': ['console'],
                'level': 'DEBUG'
            },
        }
    }
