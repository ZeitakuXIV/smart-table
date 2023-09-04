from django.contrib.auth.backends import ModelBackend
from .models import CustomUser  # Import your custom user model
import bcrypt
class CustomAuthBackend(ModelBackend):
    def authenticate(self, request, nis=None, password=None, **kwargs):
        try:
            # Use your custom query logic to retrieve the user by NIS
            user = CustomUser.objects.get(id=nis)
            print(user)
            # Check the user's password
            if(bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8'))):
                return user
        except CustomUser.DoesNotExist:
            pass  # User with the specified NIS does not exist

        return None  # Return None if authentication fails