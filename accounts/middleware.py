from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken

from django.contrib.auth import get_user_model

User = get_user_model()

@database_sync_to_async
def get_user_from_token(token_str):
    try:
        access_token = AccessToken(token_str)   #validates signature + expiry
        user_id = access_token["user_id"]   # same claim JWTAuthentication reads
        return User.objects.get(id=user_id)
    except (InvalidToken, TokenError, User.DoesNotExit):
        return AnonymousUser()

class JWTAuthMiddleware:
    """
    Replaces Channels' default session-based AuthMiddlewareStack. 
    Reads ?token=... from the WebSocket connection URL and resolves it into scope["user"], using the same JWT validation REST already trusts.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        query_string = scope.get("query_string", b"").decode()
        params = parse_qs(query_string)
        token_list = params.get("token")

        if token_list:
            scope["user"] = await get_user_from_token(token_list[0])
        else:
            scope["user"] = AnonymousUser()

        return await self.app(scope, receive, send)
