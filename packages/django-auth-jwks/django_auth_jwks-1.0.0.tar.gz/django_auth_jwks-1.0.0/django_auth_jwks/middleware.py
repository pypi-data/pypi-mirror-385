from django.http import JsonResponse
from .verifier import verify_token

class AuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1]
            try:
                claims = verify_token(token)
                request.user_claims = claims
            except Exception as e:
                return JsonResponse({"error": str(e)}, status=401)
        return self.get_response(request)
