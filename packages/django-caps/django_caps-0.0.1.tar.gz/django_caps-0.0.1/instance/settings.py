"""Django settings for ox.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/access/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


DEBUG = True
ALLOWED_HOSTS = ["127.0.0.1"]


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-bg*enkwcea%4xjcvkpbb_h@6#ue78#t1q(z^w@faagal7**^9i"


# Application definition
INSTALLED_APPS = [
    "caps",
    "tests.app",
    "rest_framework",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "caps.middleware.AgentMiddleware",
]

ROOT_URLCONF = "instance.urls"
SITE_ID = 1

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "caps" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# ASGI_APPLICATION = "ox.asgi.application"
WSGI_APPLICATION = "instance.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.0/access/settings/#databases
DATABASES = {
    "dev": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.dev.sqlite3",
    },
    #    "prod": {
    #        "NAME": "ox",
    #        "ENGINE": "django.db.backends.postgresql",
    #        "USER": "ox",
    #        "PASSWORD": "",
    #    },
}
DATABASES["default"] = DATABASES["dev"]


# Password validation
# https://docs.djangoproject.com/en/5.0/access/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "caps.backends.PermissionsBackend",
]

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Note: we use a generic name to be agnostic with frontend applications
LANGUAGE_COOKIE_NAME = "lang"


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/
STATIC_URL = "/static/"


# Default primary key field type
# https://docs.djangoproject.com/en/5.0/access/settings/#default-auto-field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 50,
}
