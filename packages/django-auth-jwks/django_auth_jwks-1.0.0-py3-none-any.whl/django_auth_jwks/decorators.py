from django.http import JsonResponse
from functools import wraps
from .verifier import verify_token

def require_auth(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return JsonResponse({"error": "Missing bearer token"}, status=401)

        token = auth_header.split(" ", 1)[1]
        try:
            claims = verify_token(token)
            request.user_claims = claims
            return view_func(request, *args, **kwargs)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=401)

    return wrapper
