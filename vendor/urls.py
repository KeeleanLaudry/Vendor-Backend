from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    request_otp,
    verify_otp,
    upload_profile,
    get_vendor_profile,
    VendorServicePricingViewSet
)

router = DefaultRouter()
router.register("pricing", VendorServicePricingViewSet, basename="vendor-pricing")

urlpatterns = [
    # 🔐 Auth / Profile
    path("request-otp/", request_otp),
    path("verify-otp/", verify_otp),
    path("upload-profile/", upload_profile),
    path("get-profile/", get_vendor_profile),

    # 💰 Vendor Pricing APIs
    path("", include((router.urls, "vendor"), namespace="vendor")),
]