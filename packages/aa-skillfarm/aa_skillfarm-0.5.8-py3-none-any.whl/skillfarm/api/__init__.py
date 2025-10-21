# Third Party
from ninja import NinjaAPI
from ninja.security import django_auth

# Django
from django.conf import settings

# AA Skillfarm
from skillfarm.api import character

api = NinjaAPI(
    title="Geuthur API",
    version="0.2.0",
    urls_namespace="skillfarm:api",
    auth=django_auth,
    csrf=True,
    openapi_url=settings.DEBUG and "/openapi.json" or "",
)

# Add the character endpoints
character.setup(api)
