from .base import *  # noqa
from .base import env  # noqa: E501

# warnigns for linters code - E501 for unused variables


# Django project general settings.
ADMINS = [("Mahboob Alam", "connect.mahboobalam@gmail.com")]
SECRET_KEY = env("DJANGO_SECRET_KEY")
ADMIN_URL = env("ADMIN_URL")



# Django security settings.
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["cutetube.algocode.site"])
# ALLOWED_HOSTS = ["127.0.0.1"]

# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:8000",
#     "http://127.0.0.1:8000",
#     "http://127.0.0.1:5500",
#     "http://127.0.0.1:8080",
# ]

CSRF_TRUSTED_ORIGINS = [
    "https://cutetube.algocode.site",
    "https://algocode.site",
    # "http://127.0.0.1:8000",
    # "http://127.0.0.1:5500",
    # "http://127.0.0.1:8080",
]


# CORS_ALLOW_ALL_ORIGINS = True

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SECURE_SSL_REDIRECT = env("DJANGO_SECURE_SSL_REDIRECT", default=True)

# TODO check if cookie is used. else false.
SESSION_COOKIE_SECURE = True

CSRF_COOKIE_SECURE = True

# TODO caution. 518400 seconds as 6 days. use wisely.
SECURE_HSTS_SECONDS = 60

SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool(
    "DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS", default=True
)

SECURE_CONTENT_TYPE_NOSNIFF = env.bool(
    "DJANGO_SECURE_CONTENT_TYPE_NOSNIFF", default=True
)

# Static file content host
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

SITE_NAME = "CuteTube - A YouTube Mimick Scalable VoD Backend!"


# AWS S3 Config for VoD Files.
AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME = env("AWS_S3_REGION_NAME")


# Redis
REDIS_CACHE_HOST = env("REDIS_CACHE_HOST")
REDIS_CACHE_RATELIMIT_DB_INDEX = int(env("REDIS_CACHE_RATELIMIT_DB_INDEX"))
REDIS_CELERY_RESULT_BACKEND_DB_INDEX = int(env("REDIS_CELERY_RESULT_BACKEND_DB_INDEX"))

# redis cache timeout for Stream and Upload api rate limit
REDIS_RATE_LIMIT_CACHE_TIME_IN_SECONDS = int(
    env("REDIS_RATE_LIMIT_CACHE_TIME_IN_SECONDS")
)


########################################################
# logging

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}},
    "formatters": {
        "verbose": {
            "format": "%(levelname)s  %(asctime)s %(module)s  %(process)d %(thread)d %(message)s "
        }
    },
    "handlers": {
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console"],
    },
    "loggers": {
        "django.request": {  # only used when debug=false
            "handlers": ["mail_admins"],
            "level": "ERROR",
            "propagate": True,
        },
        "django.security.DisallowedHost": {  # only used when debug=false
            "handlers": ["console", "mail_admins"],
            "level": "ERROR",
            "propagate": True,
        },
    },
    # uncomment for django database query logs
    # 'loggers': {
    #     'django.db': {
    #         'level': 'DEBUG',
    #         'handlers': ['console'],
    #     }
    # }
}
