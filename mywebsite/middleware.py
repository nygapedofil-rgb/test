# middleware.py
import jwt
from urllib.parse import parse_qs
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async

User = get_user_model()

@database_sync_to_async
def get_user(user_id):
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return AnonymousUser()


class JWTAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):   # ← MUSI mieć 3 argumenty
        query_string = scope["query_string"].decode()
        query_params = parse_qs(query_string)

        token = query_params.get("token")

        if token:
            token = token[0]
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                scope["user"] = await get_user(payload["user_id"])
            except Exception as e:
                print('jwt error', e)
                scope["user"] = AnonymousUser()
        else:
            scope["user"] = AnonymousUser()

        return await self.app(scope, receive, send)