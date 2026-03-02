from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed


class IsAdminJWT(BasePermission):
    def has_permission(self, request, view):
        auth = JWTAuthentication()

        try:
            validated_token = auth.get_validated_token(
                auth.get_raw_token(
                    auth.get_header(request)
                )
            )
        except Exception:
            raise AuthenticationFailed("Invalid or expired token")

        if validated_token.get("role") != "admin":
            raise AuthenticationFailed("Admin access required")

        return True