from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User

from rest_framework import authentication, exceptions

from rownd_django.auth import client

class RowndAuthError(Exception):
    pass

class RowndAuthBackend:
    def _authenticate(self, token: str):
        if not token:
            return None
            
        try:
            token_info = client.validate_jwt(token)
            user = User.objects.get(username=token_info["sub"])
            return user
        except User.DoesNotExist:
            # fetch user from Rownd
            try:
                rownd_user = client.fetch_user(token_info["https://auth.rownd.io/app_user_id"])
                user = User.objects.get(email=rownd_user["data"]["email"])
                return user
            except User.DoesNotExist:
                # create the user
                try:
                    user = User(username=token_info["sub"], email=rownd_user["data"]["email"], first_name=rownd_user["data"].get("first_name", ""), last_name=rownd_user["data"].get("last_name", ""))
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
            print(e)
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