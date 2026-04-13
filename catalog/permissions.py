from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed


class IsAdminOrDjangoStaff(BasePermission):
    """
    FOR WRITE OPERATIONS (POST, PUT, PATCH, DELETE):
    - User must have valid JWT with role='admin' (Admin API)
    - OR User is authenticated via Django session with is_staff=True (Django Admin Panel)
    
    This permission is ONLY used for write operations.
    For read operations, the view uses IsAuthenticated() instead.
    """
    
    def has_permission(self, request, view):
        # ✅ Check Django Admin session authentication (uses Vendor model)
        if request.user and request.user.is_authenticated:
            # Check if it's a Vendor with staff access
            if hasattr(request.user, 'is_staff') and request.user.is_staff:
                return True
            if hasattr(request.user, 'is_superuser') and request.user.is_superuser:
                return True
        
        # ✅ Check JWT authentication with admin role
        # This handles AdminUser JWT tokens from /api/accounts/admin-login/
        auth = JWTAuthentication()
        
        try:
            # Get the JWT token from header
            raw_token = auth.get_raw_token(auth.get_header(request))
            if raw_token:
                # Validate the token
                validated_token = auth.get_validated_token(raw_token)
                
                # Check if role is admin
                if validated_token.get("role") == "admin":
                    # ✨ IMPORTANT: Don't try to get the user from database
                    # Just verify the token has admin role
                    # The user_id in the token is for AdminUser, not Vendor
                    return True
                    
        except Exception as e:
            # JWT validation failed
            pass
        
        # ❌ No valid admin authentication found
        return False