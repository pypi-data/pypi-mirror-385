from django.conf import settings

DEFAULTS = {
    "ISSUER": None,
    "JWKS_URI": None,
    "AUDIENCE": None,
    "CACHE_TTL": 300,
    "CLOCK_SKEW": 60,
}

def get_setting(name):
    return getattr(settings, "AUTH_JWKS", {}).get(name, DEFAULTS[name])
