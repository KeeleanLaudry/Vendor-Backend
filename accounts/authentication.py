# accounts/authentication.py

from rest_framework_simplejwt.authentication import JWTAuthentication


class AdminVendorJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        """
        🔥 DO NOT fetch user from DB
        Fixes: 'user not found'
        """

        class TokenUser:
            def __init__(self, token):
                self.id = token.get("user_id")
                self.role = token.get("role")
                self.is_authenticated = True

            def __str__(self):
                return f"{self.role}-{self.id}"

        return TokenUser(validated_token)