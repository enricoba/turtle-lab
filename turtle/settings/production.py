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


from .base import *


DEBUG = False
ALLOWED_HOSTS = ['{}'.format(os.environ.get('ALLOWED_HOSTS'))]

# SSL settings
CSRF_COOKIE_SECURE = bool(int(os.environ.get('CSRF_COOKIE_SECURE')))
CSRF_USE_SESSIONS = bool(int(os.environ.get('CSRF_USE_SESSIONS')))
SESSION_COOKIE_SECURE = bool(int(os.environ.get('SESSION_COOKIE_SECURE')))
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_CONTENT_TYPE_NOSNIFF = bool(int(os.environ.get('SECURE_CONTENT_TYPE_NOSNIFF')))
SECURE_HSTS_SECONDS = int(os.environ.get('SECURE_HSTS_SECONDS'))
SECURE_BROWSER_XSS_FILTER = bool(int(os.environ.get('SECURE_BROWSER_XSS_FILTER')))
SECURE_HSTS_INCLUDE_SUBDOMAINS = bool(int(os.environ.get('SECURE_HSTS_INCLUDE_SUBDOMAINS')))
SECURE_SSL_REDIRECT = bool(int(os.environ.get('SECURE_SSL_REDIRECT')))
SECURE_HSTS_PRELOAD = bool(int(os.environ.get('SECURE_HSTS_PRELOAD')))

# Database
with open(SECURITY_DIR + '/credentials/postgres-user') as f:
    POSTGRES_USER = f.read().strip()

with open(SECURITY_DIR + '/credentials/postgres-password') as f:
    POSTGRES_PASSWORD = f.read().strip()

with open(SECURITY_DIR + '/credentials/postgres-db') as f:
    POSTGRES_DB = f.read().strip()

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': POSTGRES_DB,
        'USER': POSTGRES_USER,
        'PASSWORD': POSTGRES_PASSWORD,
        'HOST': 'postgres',
        'PORT': 5432
    }
}
