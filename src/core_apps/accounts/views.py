from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from django.db import IntegrityError

from rest_framework.views import APIView, api_settings
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import status


from core_apps.accounts.serializers import UserRegistrationAPISerializer
from core_apps.accounts.renderers import UserJSONRenderer, MultiUserJSONRenderer
from core_apps.accounts.utils import get_jwt_token


class UserRegistrationAPI(APIView):
    """API for User Registration"""

    renderer_classes = [UserJSONRenderer]

    def post(self, request):
        serializer = UserRegistrationAPISerializer(data=request.data)

        try:
            if serializer.is_valid(raise_exception=True):
                user = serializer.save()
                token = get_jwt_token(user_obj=user)
                return Response(
                    {"status": "success", "token": token}, status=status.HTTP_200_OK
                )
            return Response(
                {"status": "error", "detail": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ValidationError as ve:
            return Response(
                {"status": "error", "detail": ve.detail},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except IntegrityError as ie:
            return Response(
                {
                    "status": "error",
                    "detail": "A user with this username already exists!",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            return Response(
                {"status": "error", "detail": "Something went wrong at our end!"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UserLoginAPI(APIView):
    """API for User Login in CuteTube Platform"""

    renderer_classes = [UserJSONRenderer]

    def post(self, request):

        # Credential can be either "email" or "username"
        credential = request.data.get("credential", None)
        password = request.data.get("password", None)

        if not credential:
            return Response(
                {"status": "error", "detail": "email or username is not provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not password:
            return Response(
                {"status": "error", "detail": "password is not provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Custom auth backend is used.
        user = authenticate(request=request, email=credential, password=password)

        if user is None:
            user = authenticate(request=request, username=credential, password=password)

        if user:
            token = get_jwt_token(user_obj=user)
            return Response(
                {"status": "success", "token": token}, status=status.HTTP_200_OK
            )
        
        return Response(
                {
                    "status": "error",
                    "detail": {"non_field_errors": ["Username, Email or password is incorrect"]},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
