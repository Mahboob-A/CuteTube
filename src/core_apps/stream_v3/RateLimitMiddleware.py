# pyhton
import time
import logging

# django
from django.http import JsonResponse
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from rest_framework.status import HTTP_429_TOO_MANY_REQUESTS

# redis
import redis

logger = logging.getLogger(__name__)

try:
    redis_client = redis.Redis(
        host=settings.REDIS_CACHE_HOST,
        port=6379,
        db=settings.REDIS_CACHE_RATELIMIT_DB_INDEX,  # 0 Index for Celery. 1 for Ratelimit.
    )
    print("settings.REDIS_CACHE_HOST: ", settings.REDIS_CACHE_HOST)
except (redis.ConnectionError, ImproperlyConfigured, Exception) as e:
    logger.exception(
        f"\n[Redis Import Error]: Error Occurred During Importing Reids In RateLimit Middleware\n[EXCEPTION]: {str(e)}"
    )
    raise ImproperlyConfigured("Redis is not available")


class VODStreamAndUploadAPIRateLimitMiddleware:
    """Rate Limit Middleware for Stream and Upload APIs of CuteTube.

    Algorithm: TokenBucket Algorithm

    Rules:
        For each 60 seconds, a new token is added in the bucket.

    """

    VOD_APIS_RATE_LIMIT = {
        "/api/v3/vod/metadata/stream/": {
            "max_tokens": 3,
            "refill_rate": 1.0 / 20.0,  # 1 token every 20 seconds
        },
        "/api/v3/vod/initiate-task/upload/": {
            "max_tokens": 1,  # only one token per cycle 
            "refill_rate": 1.0 / 1200.0,  # 1 token every 20 minutes
        },
    }

    def __init__(self, get_response) -> None:
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get(
            "HTTP_X_FORWARDED_FOR"
        )  # in case of proxy or load balancer
        if x_forwarded_for:
            ip_addr = x_forwarded_for.split(",")[0]
        else:
            ip_addr = request.META.get("REMOTE_ADDR")

        return ip_addr

    def process_view(self, request, view_func, view_args, view_kwargs):
        """The process_view method will be processed just before the actual view is called.
        This is 'request phase' hook.
        """

        for paths, limits in self.VOD_APIS_RATE_LIMIT.items():
            if request.path.startswith(paths):

                client_ip = self.get_client_ip(request=request)
                rate_limit_key = (
                    f"{paths}:{client_ip}"  # /api/v3/vod/metadata/stream/:43.23.78.23
                )

                max_tokens = limits["max_tokens"]
                refill_rate = limits["refill_rate"]

                try:
                    bucket = redis_client.get(rate_limit_key)
                except (redis.ConnectionError, ImproperlyConfigured, Exception) as e:
                    logger.exception(
                        f"\n[Redis Import Error]: Error occurred during connecting to Redis in RateLimitMiddleware\n[EXCEPTION]: {str(e)}"
                    )
                    raise ImproperlyConfigured(
                        "Redis is not configured or Improperly configured."
                    )
                curr_time = time.time()

                if bucket is None:
                    bucket = {"tokens": max_tokens, "last_request_time": curr_time}
                else:
                    bucket = eval(bucket)  # str to dict
                    elapsed_time = curr_time - bucket["last_request_time"]
                    new_tokens = elapsed_time * refill_rate
                    bucket["tokens"] = min(max_tokens, bucket["tokens"] + new_tokens)
                    bucket["last_request_time"] = curr_time

                # checking token availability
                if bucket["tokens"] >= 1:
                    bucket["tokens"] -= 1
                    redis_client.set(
                        rate_limit_key,
                        str(bucket),
                        ex=settings.REDIS_RATE_LIMIT_CACHE_TIME_IN_SECONDS,
                    )
                else:
                    wait_time_for_new_request = (1 - bucket["tokens"]) / refill_rate
                    return JsonResponse(
                        {
                            "status_code": 429,
                            "status": "too-many-requests",
                            "data": {
                                "message": "Rate limit exceed. Pleas wait before making another request.",
                                "wait_time": f"{wait_time_for_new_request:.2f} seconds",
                            },
                        },
                        status=HTTP_429_TOO_MANY_REQUESTS,
                    )

        # process the other middleware or view
        return None
