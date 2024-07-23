import threading
import boto3

from django.conf import settings

from celery.signals import worker_process_init


"""
Note: 

Alghouth Celery works in multiprocessing way internally by default and has little to do with threading, but 
I am trying to create a single S3 Client per Celery Process. 

I am using  "worker_process_init" signal of clelery to create a S3 Client, but I do not want to use any Global Variable. 

Hence, I am creating a singleton class for easier access of S3 Client per Celery Worker Process and without using any Global variable. 
"""


class SingletonMeta(type):
    """A metaclass for making a class as a Singleton."""

    _instance = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        # Using __call__ instead of __new__ as I want to separate the singleton logic  from main S3 Client class.
        if cls not in cls._instance:
            with cls._lock:
                if cls not in cls._instance:
                    instance = super().__call__(*args, **kwargs)
                    cls._instance[cls] = instance
        return cls._instance[cls]


class S3Client_VoDData_Singleton(metaclass=SingletonMeta):
    """Singleton class for S3 Client for VoD data Configuration"""

    def __init__(self):
        self._client = None

    def initialize(self):
        if self._client is None:
            self._client = boto3.client(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME,
            )

    def get_client(self):
        if self._client is None:
            self.initialize()
        return self._client


s3_client_vod_data_singleton = S3Client_VoDData_Singleton()
