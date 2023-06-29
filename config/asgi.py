import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
import battle.routing
from urllib.parse import parse_qs
from rest_framework_simplejwt.authentication import JWTAuthentication
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")


class JwtTokenAuthMiddleware(BaseMiddleware):
    """JWT토큰인증 미들웨어

    웹소켓 요청에 대해 JWT토큰 사용자 인증을 처리합니다.
    """

    async def __call__(self, scope, receive, send):
        await self.authenticate(scope)
        return await super().__call__(scope, receive, send)

    @database_sync_to_async
    def authenticate(self, scope):
        queries = parse_qs(scope["query_string"].strip().decode())
        raw_token = queries["token"][0]
        page = queries["page"][0]
        auth = JWTAuthentication()
        validated_token = auth.get_validated_token(raw_token)
        user = auth.get_user(validated_token)
        scope["user"] = user
        scope["page"] = page


application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AllowedHostsOriginValidator(
            JwtTokenAuthMiddleware(URLRouter(battle.routing.websocket_urlpatterns))
        ),
    }
)
