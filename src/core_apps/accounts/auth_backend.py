from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.http import HttpRequest


class EmailUsernameAuthBackend(ModelBackend):
    """A custom authentication backend for authenticate using email and username"""

    def authenticate(self, request, email=None, username=None, password=None, **kwargs):
        User = get_user_model()
        print(f"in auth backend: Username: {username}    |  email: {email}", )
        if username:
            try:
                print("in auth if username: ", username)
                user = User.objects.get(username=username)
            except User.DoesNotExist: 
                return None 
        elif email: 
            try:
                print("in elif email: ", email)
                user = User.objects.get(email=email)
            except User.DoesNotExist: 
                return None 
  
        if user.check_password(raw_password=password):
            return user 
        return None 
