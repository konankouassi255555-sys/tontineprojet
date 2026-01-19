# Production Settings Configuration for Django on Render

## Installation des packages

```bash
pip install gunicorn whitenoise python-dotenv psycopg2-binary
```

## Mise à jour de settings.py

Remplacez votre `config/settings.py` par cette configuration:

```python
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# SECRET KEY
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-change-this-in-production')

# DEBUG
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# ALLOWED HOSTS
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# CSRF TRUSTED ORIGINS
CSRF_TRUSTED_ORIGINS = [f"https://{host}" for host in ALLOWED_HOSTS]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
    'tontines',
    'core',
]

MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',  # ← WhiteNoise FIRST
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

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

# DATABASE - Production PostgreSQL or Development SQLite
DATABASE_URL = os.getenv('DATABASE_URL')

if DATABASE_URL:
    # Production - PostgreSQL
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # Development - SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# PASSWORD VALIDATION
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

# INTERNATIONALIZATION
LANGUAGE_CODE = 'fr-FR'
TIME_ZONE = 'Africa/Dakar'
USE_I18N = True
USE_TZ = True

# STATIC FILES
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# MEDIA FILES
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# DEFAULT PRIMARY KEY FIELD TYPE
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# SECURITY SETTINGS
if not DEBUG:
    # HTTPS
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_SECURITY_POLICY = {
        'default-src': ("'self'",),
        'style-src': ("'self'", "'unsafe-inline'", "cdn.jsdelivr.net"),
        'script-src': ("'self'", "cdn.jsdelivr.net"),
        'img-src': ("'self'", "data:"),
    }
    X_FRAME_OPTIONS = 'DENY'

# Custom User Model
AUTH_USER_MODEL = 'accounts.CustomUser'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
```

## Installation de dj-database-url

Pour faciliter la gestion de DATABASE_URL:

```bash
pip install dj-database-url
```

Ajoutez à requirements.txt:
```
dj-database-url==2.1.0
```

## Variables d'environnement pour Render

Configurez sur Render Dashboard:

```
DEBUG=False
SECRET_KEY=your-secret-key-here-minimum-50-characters
ALLOWED_HOSTS=tontinepro.onrender.com,localhost,127.0.0.1
DATABASE_URL=postgresql://user:password@host:port/dbname
PYTHON_VERSION=3.13.1
```

## Vérification locale

Avant de déployer, testez localement:

```bash
# Avec .env configuré
DEBUG=False python manage.py runserver

# Collectez les statiques
python manage.py collectstatic --noinput

# Vérifiez que STATIC_ROOT a les fichiers
ls staticfiles/
```

## Troubleshooting

### Static files not loading
```bash
python manage.py collectstatic --noinput --clear
```

### Database connection error
```bash
# Vérifiez DATABASE_URL
echo $DATABASE_URL

# Test de connexion
psql $DATABASE_URL
```

### Import errors
```bash
pip install -r requirements.txt
python manage.py check
```
