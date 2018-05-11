"""
turtle-lab.org
Copyright (C) 2017  Henrik Baran

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

# python imports
import os

# django imports
from django.core.exceptions import ImproperlyConfigured

# app imports
import lab.custom as custom


# function for required settings from environment variable
def _require_env(env):
    """Raise an error if environment variable is not defined.

    :param env: environment variable
    :type env: str
    :return: returns string or integer of env variable
    :rtype: str/int
    """
    if not isinstance(env, str):
        raise TypeError('Argument of type string expected.')
    raw_value = os.getenv(env)
    if raw_value is None:
        raise ImproperlyConfigured('Required environment variable "{}" is not set.'.format(env))
    try:
        return custom.value_to_int(raw_value)
    except ValueError:
        return raw_value


# function for required settings from local files
def _require_file(path, file_name):
    """Raise an error if file for configuration not existing or empty

    :param path: absolute path to file ending with /
    :type path: str
    :param file_name: file name
    :type file_name: str
    :return: returns string of file content
    :rtype: str
    """
    if not isinstance(path, str) or not isinstance(file_name, str):
        raise TypeError('Argument of type string expected.')
    try:
        with open(path + file_name) as local_file:
            content = local_file.read().strip()
            if content:
                return content
            else:
                raise ImproperlyConfigured('File "{}" is empty.'.format(file_name))
    except FileNotFoundError:
        raise


#########
# PATHS #
#########

# base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# security directory for storing secrets in permission controlled files
SECURITY_DIR = os.path.join(BASE_DIR, 'security')
# log directory
LOG_DIR = os.path.join(BASE_DIR, 'logs')
# files dir
FILES_DIR = os.path.join(BASE_DIR, 'lab')
# media root for labels
MEDIA_ROOT = os.path.join(BASE_DIR, 'labels')
# static files dir
STATIC_DIR = os.path.join(BASE_DIR, 'static')


###########
# SECRETS #
###########

# django secret key
SECRET_KEY = _require_file(path=SECURITY_DIR + '/keys/', file_name='SECRET_KEY')
SECRET = _require_file(path=SECURITY_DIR + '/keys/', file_name='SECRET')
POSTGRES_USER = _require_file(path=SECURITY_DIR + '/credentials/', file_name='POSTGRES_USER')
POSTGRES_PASSWORD = _require_file(path=SECURITY_DIR + '/credentials/', file_name='POSTGRES_PASSWORD')


##########################
# APPS MODULES AND SO ON #
##########################

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'lab.apps.LabConfig',
    'widget_tweaks',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend'
]

AUTH_USER_MODEL = 'lab.Users'

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
]


ROOT_URLCONF = 'turtle.urls'
LOGIN_URL = '/'
LOGIN_REDIRECT_URL = '/'

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

WSGI_APPLICATION = 'turtle.wsgi.application'

# Password validation
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

#####################
# LANGUAGE AND TIME #
#####################

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


########
# URLS #
########

MEDIA_URL = '/labels/'
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    STATIC_DIR,
]

#########
# CACHE #
#########

if os.environ.get('CACHE', 0):
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "redis://redis:6379/0",
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "COMPRESSOR": "django_redis.compressors.zlib.ZlibCompressor",
            }
        }
    }

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

############
# DATABASE #
############

# postgres settings
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': _require_env('POSTGRES_DB'),
        'USER': POSTGRES_USER,
        'PASSWORD': POSTGRES_PASSWORD,
        'HOST': os.environ.get('POSTGRES_HOST', 'localhost'),
        'PORT': os.getenv('POSTGRES_PORT', 5432)
    }
}


####################
# FLAGS AND VALUES #
####################

# general settings
DEBUG = custom.value_to_bool(_require_env('DEBUG'))
ALLOWED_HOSTS = ['{}'.format(_require_env('ALLOWED_HOSTS'))]
CONN_MAX_AGE = None

# security settings of type bool
CSRF_COOKIE_SECURE = custom.value_to_bool(os.environ.get('CSRF_COOKIE_SECURE', 0))
CSRF_USE_SESSIONS = custom.value_to_bool(os.environ.get('CSRF_USE_SESSIONS', 0))
SESSION_COOKIE_SECURE = custom.value_to_bool(os.environ.get('SESSION_COOKIE_SECURE', 0))
SECURE_CONTENT_TYPE_NOSNIFF = custom.value_to_bool(os.environ.get('SECURE_CONTENT_TYPE_NOSNIFF', 0))
SECURE_BROWSER_XSS_FILTER = custom.value_to_bool(os.environ.get('SECURE_BROWSER_XSS_FILTER', 0))
SECURE_HSTS_INCLUDE_SUBDOMAINS = custom.value_to_bool(os.environ.get('SECURE_HSTS_INCLUDE_SUBDOMAINS', 0))
SECURE_SSL_REDIRECT = custom.value_to_bool(os.environ.get('SECURE_SSL_REDIRECT', 0))
SECURE_HSTS_PRELOAD = custom.value_to_bool(os.environ.get('SECURE_HSTS_PRELOAD', 0))

# security settings of type integer
SECURE_HSTS_SECONDS = custom.value_to_int(os.environ.get('SECURE_HSTS_SECONDS', 0))
SESSION_COOKIE_AGE = custom.value_to_int(os.environ.get('SESSION_COOKIE_AGE', 3600))

# security settings of type tuple
if os.environ.get('SECURE_PROXY_SSL_HEADER', 0):
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# security settings of type string
X_FRAME_OPTIONS = os.environ.get('X_FRAME_OPTIONS', 'SAMEORIGIN')

###########
# LOGGING #
###########

# logging settings
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_DIR + '/default.log',
            'maxBytes': 1024*1024*5,  # 5 MB
            'backupCount': 5,
            'formatter': 'standard'
        },
        'request': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_DIR + '/request.log',
            'maxBytes': 1024*1024*5,  # 5 MB
            'backupCount': 5,
            'formatter': 'standard'
        },
        'server': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_DIR + '/server.log',
            'maxBytes': 1024*1024*5,  # 5 MB
            'backupCount': 5,
            'formatter': 'standard'
        },
        'template': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_DIR + '/template.log',
            'maxBytes': 1024*1024*5,  # 5 MB
            'backupCount': 5,
            'formatter': 'standard'
        },
        'db.backends': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_DIR + '/backends.log',
            'maxBytes': 1024*1024*5,  # 5 MB
            'backupCount': 5,
            'formatter': 'standard'
        },
        'security': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_DIR + '/security.log',
            'maxBytes': 1024*1024*5,  # 5 MB
            'backupCount': 5,
            'formatter': 'standard'
        },
        'db.backends.schema': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_DIR + '/schema.log',
            'maxBytes': 1024*1024*5,  # 5 MB
            'backupCount': 5,
            'formatter': 'standard'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
    },
    'loggers': {
        'lab': {
            'handlers': ['default', 'console'],
            'level': 'DEBUG',
            'propagate': True
        },
        'django.request': {
            'handlers': ['request', 'console'],
            'level': 'DEBUG',
            'propagate': False
        },
        'django.template': {
            'handlers': ['template'],
            'level': 'DEBUG',
            'propagate': False
        },
        'django.server': {
            'handlers': ['server'],
            'level': 'DEBUG',
            'propagate': False
        },
        'django.db.backends': {
            'handlers': ['db.backends'],
            'level': 'DEBUG',
            'propagate': False
        },
        'django.security.*': {
            'handlers': ['security'],
            'level': 'DEBUG',
            'propagate': False
        },
        'django.db.backends.schema': {
            'handlers': ['db.backends.schema'],
            'level': 'DEBUG',
            'propagate': False
        }
    }
}
