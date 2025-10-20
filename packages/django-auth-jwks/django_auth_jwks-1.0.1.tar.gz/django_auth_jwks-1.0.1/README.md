# django-auth-jwks

**django-auth-jwks** is a reusable Django app for verifying JWT tokens via JSON Web Key Sets (JWKS) with caching support. It is designed to work seamlessly with Django REST Framework (DRF) and supports both database-backed and stateless authentication scenarios.

> **Note**: This package is currently in **beta**. Features and APIs may change in future releases.

## Features

- **JWT Verification**: Validate JWT tokens using JWKS.
- **Stateless Authentication**: Supports servers without a database or user model.
- **Database Integration**: Maps JWT claims to Django user models when available.
- **Caching**: Efficiently caches JWKS for improved performance.
- **DRF Integration**: Works with Django REST Framework for API authentication.

## Installation

Install the package using pip:

```bash
pip install django-auth-jwks
```

Alternatively, for development purposes, you can install it in editable mode:

```bash
pip install -e .
```

To uninstall the package:

```bash
pip uninstall django-auth-jwks
```

## Quickstart

1. Add `django_auth_jwks` to your `INSTALLED_APPS` in `settings.py`:

   ```python
   INSTALLED_APPS = [
       ...,
       "django_auth_jwks",
   ]
   ```

2. Configure the `AUTH_JWKS` setting in your Django project to point to your JWKS URL:

   ```python
   AUTH_JWKS = {
        "ISSUER": "https://example.com",
        "JWKS_ENDPOINT": "/o/.well-known/jwks.json",
        "AUDIENCE": "example-service",
        "CACHE_TTL": 300,
    }
   ```

3. Use the `JWTAuthentication` class in your DRF settings:

   ```python
   REST_FRAMEWORK = {
       "DEFAULT_AUTHENTICATION_CLASSES": [
           "django_auth_jwks.authentication.JWTAuthentication",
       ],
   }
   ```

4. Optionally, use the `@require_auth` decorator or middleware for securing views.

5. Run your Django server:

   ```bash
   python manage.py runserver
   ```

## Usage

### Securing Views with the `@require_auth` Decorator

You can secure individual views by applying the `@require_auth` decorator:

```python
from django_auth_jwks.decorators import require_auth

@require_auth
def my_view(request):
    return JsonResponse({"message": "Authenticated!"})
```

### Using Middleware for Global Authentication

To apply authentication globally, add the middleware to your `MIDDLEWARE` setting:

```python
MIDDLEWARE = [
    ...,
    "django_auth_jwks.middleware.JWTAuthenticationMiddleware",
]
```

## Development

To contribute to this project:

1. Clone the repository.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## Disclaimer

This package is in **beta**. Use it in production environments with caution, and report any issues you encounter.
