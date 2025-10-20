from django.conf import settings

DEFAULTS = {
    "ISSUER": None,
    "JWKS_ENDPOINT": "/o/.well-known/jwks.json",
    "AUDIENCE": None,
    "CACHE_TTL": 300,
}

def get_setting(name):
    return getattr(settings, "AUTH_JWKS", {}).get(name, DEFAULTS[name])
