# from jose import jwt
# from jose.exceptions import JWTError, ExpiredSignatureError
from .settings import get_setting
# from .cache import jwk_cache
# import requests

import jwt
from jwt import PyJWKClient, InvalidTokenError
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions

# Create a singleton instance of PyJWKClient
_jwks_client = PyJWKClient(
    f"{get_setting("ISSUER")}/o/.well-known/jwks.json",
    cache_keys=True,
    lifespan=get_setting("CACHE_TTL")
)

# def verify_token(token):
#     jwks_uri = get_setting("JWKS_URI")
#     issuer = get_setting("ISSUER")
#     audience = get_setting("AUDIENCE")
#     keys = jwk_cache.get_keys(jwks_uri)

#     try:
#         header = jwt.get_unverified_header(token)
#     except JWTError:
#         raise ValueError("Invalid token header")

#     key = next((k for k in keys if k["kid"] == header.get("kid")), None)
#     if not key:
#         raise ValueError("Matching JWK not found")

#     try:
#         claims = jwt.decode(
#             token,
#             key,
#             algorithms=[header.get("alg", "RS256")],
#             audience=audience,
#             issuer=issuer,
#         )
#         return claims
#     except ExpiredSignatureError:
#         raise ValueError("Token expired")
#     except JWTError as e:
#         raise ValueError(f"Token verification failed: {str(e)}")
    
def verify_token(token):
    issuer = get_setting("ISSUER")
    audience = get_setting("AUDIENCE")
    
    try:
        header = jwt.get_unverified_header(token)
    except InvalidTokenError:
        raise ValueError("Invalid token header")
    
    try:
        signing_key = _jwks_client.get_signing_key_from_jwt(token)

        claims = jwt.decode(
            token,
            signing_key.key,
            algorithms=[header.get("alg", "RS256")],
            audience=audience,
            issuer=issuer,
        )
        return claims
    except InvalidTokenError as e:
        raise exceptions.AuthenticationFailed(f"Invalid token: {str(e)}")
    # except ExpiredSignatureError:
    #     raise ValueError("Token expired")
    # except JWTError as e:
    #     raise ValueError(f"Token verification failed: {str(e)}")
    except Exception as e:
        raise exceptions.AuthenticationFailed(f"Token validation error: {str(e)}")
