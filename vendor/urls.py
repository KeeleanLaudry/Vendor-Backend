from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    # Auth & Profile
    request_otp,
    verify_otp,
    upload_profile,
    get_vendor_profile,
    
    # ✨ NEW: Pricing ViewSets
    VendorPriceViewSet,
    VendorPriceAttributeViewSet,
    VendorPriceAddOnViewSet,
    VendorPriceFoldingViewSet,
    VendorPriceCustomisationViewSet,
)

router = DefaultRouter()

# ==================================================================================
# 💰 VENDOR PRICING (Hierarchical Structure)
# ==================================================================================
router.register(r'prices', VendorPriceViewSet, basename='vendor-price')
# Endpoints:
# GET    /api/vendors/prices/                        → List all prices
# GET    /api/vendors/prices/?service_id=1           → Filter by service
# GET    /api/vendors/prices/?category_id=2          → Filter by category
# GET    /api/vendors/prices/?subcategory_id=3       → Filter by subcategory
# GET    /api/vendors/prices/{id}/                   → Get single price
# POST   /api/vendors/prices/                        → Create price
# PUT    /api/vendors/prices/{id}/                   → Update price
# DELETE /api/vendors/prices/{id}/                   → Delete price
# POST   /api/vendors/prices/bulk-create/            → Bulk upload (max 500)
# GET    /api/vendors/prices/missing-combinations/   → What's not priced yet
# GET    /api/vendors/prices/audit-log/              → Price change history


# ==================================================================================
# 🔗 VENDOR PRICE OPTIONS (Linked to VendorPrice)
# ==================================================================================
router.register(r'price-attributes', VendorPriceAttributeViewSet, basename='vendor-price-attribute')
# Endpoints:
# GET    /api/vendors/price-attributes/?vendor_price_id=1  → Attributes for a price
# POST   /api/vendors/price-attributes/                    → Add attribute option
# PUT    /api/vendors/price-attributes/{id}/               → Update attribute
# DELETE /api/vendors/price-attributes/{id}/               → Remove attribute

router.register(r'price-addons', VendorPriceAddOnViewSet, basename='vendor-price-addon')
# Endpoints:
# GET    /api/vendors/price-addons/?vendor_price_id=1  → Add-ons for a price
# POST   /api/vendors/price-addons/                    → Add add-on to price
# PUT    /api/vendors/price-addons/{id}/               → Update add-on price
# DELETE /api/vendors/price-addons/{id}/               → Remove add-on

router.register(r'price-folding', VendorPriceFoldingViewSet, basename='vendor-price-folding')
# Endpoints:
# GET    /api/vendors/price-folding/?vendor_price_id=1  → Folding options for a price
# POST   /api/vendors/price-folding/                    → Add folding option
# PUT    /api/vendors/price-folding/{id}/               → Update folding price
# DELETE /api/vendors/price-folding/{id}/               → Remove folding

router.register(r'price-customisations', VendorPriceCustomisationViewSet, basename='vendor-price-customisation')
# Endpoints:
# GET    /api/vendors/price-customisations/?vendor_price_id=1  → Customisations for a price
# POST   /api/vendors/price-customisations/                    → Add customisation
# PUT    /api/vendors/price-customisations/{id}/               → Update customisation price
# DELETE /api/vendors/price-customisations/{id}/               → Remove customisation


urlpatterns = [
    # ==================================================================================
    # 🔐 AUTHENTICATION & PROFILE
    # ==================================================================================
    path("request-otp/", request_otp, name="request-otp"),
    path("verify-otp/", verify_otp, name="verify-otp"),
    path("upload-profile/", upload_profile, name="upload-profile"),
    path("get-profile/", get_vendor_profile, name="get-profile"),

    # ==================================================================================
    # 📦 ALL VENDOR APIS
    # ==================================================================================
    path("", include(router.urls)),
]


# ==================================================================================
# ❌ REMOVED ENDPOINTS
# ==================================================================================
# These have been replaced by the new pricing structure:
#
# OLD: /api/vendors/pricing/
#   → NEW: /api/vendors/prices/
#
# OLD: /api/vendors/item-addons/
#   → NEW: /api/vendors/price-addons/ (linked to vendor_price_id)
#
# OLD: /api/vendors/item-foldings/
#   → NEW: /api/vendors/price-folding/ (linked to vendor_price_id)
#
# OLD: /api/vendors/item-customisations/
#   → NEW: /api/vendors/price-customisations/ (linked to vendor_price_id)
#
# ==================================================================================


# ==================================================================================
# 📋 COMPLETE VENDOR API ENDPOINTS
# ==================================================================================
#
# AUTH & PROFILE:
#   POST   /api/vendors/request-otp/
#   POST   /api/vendors/verify-otp/
#   POST   /api/vendors/upload-profile/
#   GET    /api/vendors/get-profile/
#
# PRICING (Main):
#   GET    /api/vendors/prices/
#   GET    /api/vendors/prices/?service_id=1&category_id=2&subcategory_id=3
#   GET    /api/vendors/prices/{id}/
#   POST   /api/vendors/prices/
#   PUT    /api/vendors/prices/{id}/
#   DELETE /api/vendors/prices/{id}/
#   POST   /api/vendors/prices/bulk-create/
#   GET    /api/vendors/prices/missing-combinations/
#   GET    /api/vendors/prices/audit-log/
#
# PRICING OPTIONS:
#   Attributes:      /api/vendors/price-attributes/
#   Add-ons:         /api/vendors/price-addons/
#   Folding:         /api/vendors/price-folding/
#   Customisations:  /api/vendors/price-customisations/
#
# ==================================================================================