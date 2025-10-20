from rest_framework.authentication import BaseAuthentication

from .verifier import verify_token

class JWTAuthentication(BaseAuthentication):
    """
    Authenticate requests using Bearer JWT access tokens validated via JWKS.
    """

    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None  # No credentials, let DRF handle as anonymous

        token = auth_header.split(" ")[1]
        payload = verify_token(token)
        user = self._get_user_from_claims(payload)
        return (user, payload)

    def _get_user_from_claims(self, claims):
        """
        Optionally map sub/client_id to Django user model.
        If no user model exists or the server is stateless, return a dummy authenticated user.
        """
        from django.contrib.auth import get_user_model
        from django.core.exceptions import ImproperlyConfigured

        class StatelessUser:
            """
            A simple user-like object for stateless authentication.
            """
            def __init__(self, username):
                self.username = username

            @property
            def is_authenticated(self):
                return True

        sub = claims.get("sub")
        if not sub:
            return None  # No subject claim, cannot identify user

        try:
            User = get_user_model()
            return User.objects.get(username=sub)
        except ImproperlyConfigured:
            # No user model configured, return a stateless authenticated user
            return StatelessUser(username=sub)
        except User.DoesNotExist:
            # User not found in the database, return a stateless authenticated user
            return StatelessUser(username=sub)
        except Exception:
            # Handle any other unexpected exceptions gracefully
            return None
