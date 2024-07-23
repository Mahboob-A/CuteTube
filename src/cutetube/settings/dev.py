from .base import *  # noqa
from .base import env  # noqa: E501

# warnigns for linters code - E501 for unused variables

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-w=&azyq3+x)_^2y6x+vf!2a+t3!llhv=68l+n6z#2p#w4t!f))"


CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:5500",
]

CORS_ALLOW_ALL_ORIGINS = True

CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:5500",
]

ALLOWED_HOSTS = ["127.0.0.1"]


# AWS S3 Config for VoD Files.
AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME = env("AWS_S3_REGION_NAME")


# Redis
REDIS_CACHE_HOST = env("REDIS_CACHE_HOST")
REDIS_CACHE_RATELIMIT_DB_INDEX = env("REDIS_CACHE_RATELIMIT_DB_INDEX")
REDIS_CELERY_RESULT_BACKEND_DB_INDEX = env("REDIS_CELERY_RESULT_BACKEND_DB_INDEX")

# redis cache timeout for Stream and Upload api rate limit
REDIS_RATE_LIMIT_CACHE_TIME_IN_SECONDS = int(
    env("REDIS_RATE_LIMIT_CACHE_TIME_IN_SECONDS")
)


# logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(name)-12s %(asctime)s %(module)s  %(process)d %(thread)d %(message)s "
        }
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["console"],
    },
    # uncomment for django database query logs
    # "loggers": {
    #     "django.db": {
    #         "level": "DEBUG",
    #         "handlers": ["console"],
    #     }
    # },
}
