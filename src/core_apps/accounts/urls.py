from django.urls import path

from core_apps.accounts.views import UserRegistrationAPI, UserLoginAPI


urlpatterns = [
    path(
        "registration/",
        UserRegistrationAPI.as_view(),
        name="user_registration_api",
    ),
    path("login/", UserLoginAPI.as_view(), name="user_login_api"),
]
