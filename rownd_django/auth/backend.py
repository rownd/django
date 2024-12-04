from django.contrib.auth.backends import BaseBackend
# Import the get_user_model function
from django.contrib.auth import get_user_model
from rest_framework import authentication, exceptions
from rownd_django.auth import client
from rownd_django.settings import rownd_settings
import traceback

User = get_user_model()  # Get the user model dynamically


class RowndAuthError(Exception):
    pass


class RowndAuthBackend:
    def _authenticate(self, token: str):
        if not token:
            return None

        try:
            token_info = client.validate_jwt(token)

            args = {
                rownd_settings.USER_MODEL_USERNAME_FIELD: token_info["sub"]
            }
            return User.objects.get(**args)
        except User.DoesNotExist:
            # fetch user from Rownd
            try:
                rownd_user_id = token_info["https://auth.rownd.io/app_user_id"]
                rownd_user = client.fetch_user(rownd_user_id)
                user = User.objects.get(email=rownd_user["data"].get("email", rownd_user_id))
                return user
            except User.DoesNotExist:
                # create the user
                try:
                    args = {
                        "email": rownd_user["data"].get("email", rownd_user_id),
                        "first_name": rownd_user["data"].get("first_name", ""),
                        "last_name": rownd_user["data"].get("last_name", "")
                    }

                    username_field = rownd_settings.USER_MODEL_USERNAME_FIELD
                    if username_field != "email":
                        args[rownd_settings.USER_MODEL_USERNAME_FIELD] = rownd_user_id

                    user = User(**args)
                    user.save()
                    return user

                except:
                    raise RowndAuthError("Failed to locate or create user")
        except Exception as e:
            # The token didn't pass validation or
            # we couldn't find the Rownd user or
            # something went wrong creating the local user
            raise RowndAuthError(e)


class RowndAuthenticationBackend(RowndAuthBackend, BaseBackend):
    def authenticate(self, request, token=None):
        try:
            return self._authenticate(token)

        except Exception as e:
            print(traceback.format_exc())
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


class RowndApiAuthentication(RowndAuthBackend, authentication.BaseAuthentication):
    def authenticate(self, request):
        try:
            token = request.headers.get("authorization")
            token = token.split(" ")[1]
            user = self._authenticate(token)
            return (user, None)

        except RowndAuthError as e:
            raise exceptions.AuthenticationFailed(e)

        except Exception as e:
            raise exceptions.AuthenticationFailed("Invalid or malformed token")
