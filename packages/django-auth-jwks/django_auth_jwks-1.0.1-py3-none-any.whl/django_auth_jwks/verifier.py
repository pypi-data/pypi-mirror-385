import jwt
from jwt import PyJWKClient, InvalidTokenError
from rest_framework import exceptions
from urllib.parse import urljoin

from .settings import get_setting

# Create a singleton instance of PyJWKClient
_jwks_client = PyJWKClient(
    urljoin(get_setting("ISSUER"), get_setting("JWKS_ENDPOINT")),
    cache_keys=True,
    lifespan=get_setting("CACHE_TTL")
)
    
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
    except Exception as e:
        raise exceptions.AuthenticationFailed(f"Token validation error: {str(e)}")
