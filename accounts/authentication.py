from rest_framework_simplejwt.authentication import JWTAuthentication


class AdminVendorJWTAuthentication(JWTAuthentication):
    """Authenticates admin tokens only"""
    
    def authenticate(self, request):
        """Returns None if not an admin token"""
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
        except Exception:
            return None
        
        # Check if this is an admin token
        role = validated_token.get("role")
        if role != "admin":
            return None  # Not an admin token
        
        # Create TokenUser
        class TokenUser:
            def __init__(self, token):
                self.id = token.get("user_id")
                self.role = token.get("role")
                self.is_authenticated = True

            def __str__(self):
                return f"{self.role}-{self.id}"

        user = TokenUser(validated_token)
        return (user, validated_token)