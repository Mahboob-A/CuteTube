"""
Django settings for cutetube project.

Generated by 'django-admin startproject' using Django 4.2.9.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path

from datetime import timedelta

import environ

env = environ.Env()

# TODO change env type to prod
ENVIRONMENT_TYPE = ".dev"


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

env.read_env(Path(str(BASE_DIR)) / f".envs/{ENVIRONMENT_TYPE}/.django")

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# core_apps entrypont
APP_DIR = BASE_DIR / "core_apps"

DEBUG = env("DJANGO_DEBUG")
if DEBUG == "True":
    DEBUG = True
else:
    DEBUG = False


# Application definition
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTH_APPS = [
    "rest_framework",
    "corsheaders",
]

LOCAL_APPS = [
    "core_apps.common",
    "core_apps.stream",
    "core_apps.stream_v2",
    "core_apps.stream_v3",
    "core_apps.accounts",
]

# Installed Apps
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTH_APPS + LOCAL_APPS


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "core_apps.stream_v3.RateLimitMiddleware.VODStreamAndUploadAPIRateLimitMiddleware",  # Middleware for VOD Stream and Upload API Rate LImit
]

ROOT_URLCONF = "cutetube.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "cutetube.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# Default DB
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Kolkata"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = str(BASE_DIR / "staticfiles")

MEDIA_URL = "/media/"
MEDIA_ROOT = str(BASE_DIR / "mediafiles")


###################### Auth and User Settings #########################################
AUTH_USER_MODEL = "accounts.CustomUser"

# DRF Settings
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    )
}

# Simple-JWT Settings
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=10080),  # 7 days 
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": False,
    "ALGORITHM": "HS256",
    "VERIFYING_KEY": "",
    "AUDIENCE": None,
    "ISSUER": None,
    "JSON_ENCODER": None,
    "JWK_URL": None,
    "LEEWAY": 0,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",
    "JTI_CLAIM": "jti",
}


#  Auth Backends
AUTHENTICATION_BACKENDS = [
    "core_apps.accounts.auth_backend.EmailUsernameAuthBackend",
    "django.contrib.auth.backends.ModelBackend",
]

# ##################### DASH Settings

# Main VoD directory.
DASH_VOD_DIR_ROOT = str(BASE_DIR / "vod-media")

# VoD Subdir where local video file is stored temporarily. Under this subdir, the video files will be stored.
DASH_LOCAL_VOD_VIDEOS_DIR_ROOT = f"{DASH_VOD_DIR_ROOT}/local-vod-videos-temp"

# VoD subdir where segment files are stored temporaliry. Under this subdir, the segment dirs will be stored.
DASH_LOCAL_VOD_SEGMENT_DIR_ROOT = f"{DASH_VOD_DIR_ROOT}/local-vod-segments-temp"

# S3 bucket root dir. Under this root dir, files are structure in S3.
# S3 File Structure: vod-media/UUID__rain-calm-video/extention/segment-files
DASH_S3_FILE_ROOT = "vod-media"


# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

############################################### Packages Settings #######################################

############################ CELERY CONFIG
CELERY_BROKER_URL = env("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
# CELERY_ACCEPT_CONTECT = ["json"]
# CELERY_TASK_SERIALIZER = "json"
# CELERY_RESULT_SERIALIZER = "json"
CELERY_RESULT_BACKEND_MAX_RETRIES = 15
CELERY_TASK_SEND_SENT_EVENT = True
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

if USE_TZ:
    CELERY_TIMEZONE = TIME_ZONE
