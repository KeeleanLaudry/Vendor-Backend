from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    request_otp,
    verify_otp,
    upload_profile,
    get_vendor_profile,
    VendorServicePricingViewSet,
    VendorItemAddOnViewSet,
    VendorItemFoldingViewSet,
    VendorItemCustomisationViewSet,
)

router = DefaultRouter()

# 💰 Vendor Pricing
router.register(r'pricing', VendorServicePricingViewSet, basename='vendor-pricing')

# ➕ Add-ons / Folding / Customisation
router.register(r'item-addons', VendorItemAddOnViewSet, basename='vendor-item-addon')
router.register(r'item-foldings', VendorItemFoldingViewSet, basename='vendor-item-folding')
router.register(r'item-customisations', VendorItemCustomisationViewSet, basename='vendor-item-customisation')


urlpatterns = [
    # 🔐 Auth / Profile
    path("request-otp/", request_otp),
    path("verify-otp/", verify_otp),
    path("upload-profile/", upload_profile),
    path("get-profile/", get_vendor_profile),

    # 📦 All Vendor APIs
    path("", include((router.urls, "vendor"), namespace="vendor")),
]