from rest_framework.exceptions import AuthenticationFailed

from accounts.services.auth_service import AuthService


class AdminAuthService:
    @staticmethod
    def login(validated_data):

        user = AuthService.login(validated_data)

        if not user.is_staff:
            raise AuthenticationFailed(
                "You are not authorized to access the admin portal."
            )

        return user
