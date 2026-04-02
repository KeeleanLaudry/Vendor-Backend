from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny

from .serializers import (
    RequestOTPSerializer,
    VerifyOTPSerializer,
    VendorProfileSerializer
)
from .models import VendorProfile


# --------------------------------
# REQUEST OTP
# --------------------------------
@api_view(['POST'])
@permission_classes([AllowAny])
def request_otp(request):
    serializer = RequestOTPSerializer(data=request.data)
    if serializer.is_valid():
        data = serializer.save()
        return Response({
            "message": "OTP sent",
            "vendor_id": data["vendor_id"]
        })
    return Response(serializer.errors, status=400)


# --------------------------------
# VERIFY OTP (JWT)
# --------------------------------
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp(request):
    serializer = VerifyOTPSerializer(data=request.data)
    if serializer.is_valid():
        return Response(serializer.save())
    return Response(serializer.errors, status=400)


# --------------------------------
# UPLOAD PROFILE (JWT Protected)
# --------------------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_profile(request):

    vendor = request.user

    profile, created = VendorProfile.objects.get_or_create(vendor=vendor)

    # Remove empty values
    data = request.data.copy()

    for key, value in list(data.items()):
        if value in ["", None]:
            data.pop(key)

    serializer = VendorProfileSerializer(
        profile,
        data=data,
        partial=True
    )

    if serializer.is_valid():
        serializer.save()

        # ✅ Mark profile as completed AFTER successful save
        profile.is_profile_completed = True
        profile.save(update_fields=["is_profile_completed"])

        return Response({
            "message": "Profile saved successfully",
            "created": created,
            "profile_completed": True
        })

    return Response(serializer.errors, status=400)
# --------------------------------
# GET PROFILE (JWT Protected)
# --------------------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_vendor_profile(request):

    vendor = request.user

    # Always create if not exists
    profile, created = VendorProfile.objects.get_or_create(vendor=vendor)

    serializer = VendorProfileSerializer(profile)
    return Response({
        "profile": serializer.data,
        "is_new": created
    })
from rest_framework import viewsets



from .models import VendorServicePricing
from .serializers import VendorServicePricingSerializer


class VendorServicePricingViewSet(viewsets.ModelViewSet):
    serializer_class = VendorServicePricingSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        return VendorServicePricing.objects.filter(
            vendor_id=self.request.user.id
        )

    def perform_create(self, serializer):
        serializer.save(vendor_id=self.request.user.id)