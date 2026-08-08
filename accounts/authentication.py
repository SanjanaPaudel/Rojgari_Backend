from datetime import timedelta

from django.utils import timezone
from rest_framework_simplejwt.authentication import JWTAuthentication

ACTIVITY_UPDATE_INTERVAL = timedelta(seconds=60)


class TrackedJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        result = super().authenticate(request)

        if result is not None:
            user, token = result
            now = timezone.now()

            if (
                not user.last_active_at
                or now - user.last_active_at > ACTIVITY_UPDATE_INTERVAL
            ):
                type(user).objects.filter(pk=user.pk).update(last_active_at=now)

        return result
