from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from .models import Vendor


class VendorJWTAuthentication(JWTAuthentication):
    """Authenticates vendor tokens only"""
    
    def authenticate(self, request):
        """Returns None if not a vendor token"""
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
        
        # Check if this is a vendor token
        vendor_id = validated_token.get("vendor_id")
        if not vendor_id:
            return None  # Not a vendor token
        
        # Get vendor
        try:
            vendor = Vendor.objects.get(id=vendor_id)
            return (vendor, validated_token)
        except Vendor.DoesNotExist:
            raise InvalidToken("Vendor not found")