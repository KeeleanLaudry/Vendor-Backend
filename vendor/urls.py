# vendor/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    # Auth & Profile
    request_otp,
    verify_otp,
    upload_profile,
    get_vendor_profile,
    
    # Pricing ViewSets
    VendorPricingViewSet,
    VendorPricingTemplateViewSet,
)

# Create router for ViewSets
router = DefaultRouter()

# ==================================================================================
# 💰 VENDOR PRICING (Spreadsheet-Style Flexible Pricing)
# ==================================================================================
router.register(r'pricing', VendorPricingViewSet, basename='vendor-pricing')
# Endpoints:
# GET    /api/vendor/pricing/                        → List all pricing rules
# GET    /api/vendor/pricing/?service_id=1           → Filter by service
# GET    /api/vendor/pricing/{id}/                   → Get single pricing
# POST   /api/vendor/pricing/                        → Create pricing rule
# PUT    /api/vendor/pricing/{id}/                   → Update pricing
# DELETE /api/vendor/pricing/{id}/                   → Delete pricing
# POST   /api/vendor/pricing/bulk_create/            → Bulk create (multi-select)
# POST   /api/vendor/pricing/bulk_update/            → Bulk update prices
# POST   /api/vendor/pricing/bulk_delete/            → Bulk delete prices
# GET    /api/vendor/pricing/stats/                  → Pricing statistics
# GET    /api/vendor/pricing/spreadsheet_view/       → Spreadsheet data view
# POST   /api/vendor/pricing/import_csv/             → Import CSV
# GET    /api/vendor/pricing/export_csv/             → Export CSV

router.register(r'pricing-templates', VendorPricingTemplateViewSet, basename='vendor-pricing-template')
# Endpoints:
# GET    /api/vendor/pricing-templates/              → List templates
# POST   /api/vendor/pricing-templates/              → Create template
# GET    /api/vendor/pricing-templates/{id}/         → Get template
# PUT    /api/vendor/pricing-templates/{id}/         → Update template
# DELETE /api/vendor/pricing-templates/{id}/         → Delete template
# POST   /api/vendor/pricing-templates/{id}/apply/   → Apply template to create pricing


urlpatterns = [
    # ==================================================================================
    # 🔐 AUTHENTICATION & PROFILE
    # ==================================================================================
    path("request-otp/", request_otp, name="request-otp"),
    path("verify-otp/", verify_otp, name="verify-otp"),
    path("upload-profile/", upload_profile, name="upload-profile"),
    path("get-profile/", get_vendor_profile, name="get-profile"),

    # ==================================================================================
    # 📦 PRICING APIS (Router URLs)
    # ==================================================================================
    path("", include(router.urls)),
]

# This creates the following endpoints:
# 
# Authentication:
# POST   /api/vendor/request-otp/              - Request OTP
# POST   /api/vendor/verify-otp/               - Verify OTP & get JWT
# 
# Profile:
# POST   /api/vendor/profile/upload/           - Upload profile
# GET    /api/vendor/profile/                  - Get profile
# 
# Pricing Management:
# GET    /api/vendor/pricing/                  - List all pricing rules
# POST   /api/vendor/pricing/                  - Create single pricing rule
# GET    /api/vendor/pricing/{id}/             - Get specific pricing rule
# PUT    /api/vendor/pricing/{id}/             - Update pricing rule
# PATCH  /api/vendor/pricing/{id}/             - Partial update pricing rule
# DELETE /api/vendor/pricing/{id}/             - Delete pricing rule
# 
# Bulk Operations:
# POST   /api/vendor/pricing/bulk_create/      - Create multiple rules
# POST   /api/vendor/pricing/bulk_update/      - Update multiple rules
# POST   /api/vendor/pricing/bulk_delete/      - Delete multiple rules
# 
# Analytics & Data:
# GET    /api/vendor/pricing/stats/            - Get pricing statistics
# GET    /api/vendor/pricing/spreadsheet_view/ - Get spreadsheet data
# 
# Import/Export:
# POST   /api/vendor/pricing/import_csv/       - Import CSV
# GET    /api/vendor/pricing/export_csv/       - Export CSV
# 
# Templates:
# GET    /api/vendor/pricing-templates/        - List templates
# POST   /api/vendor/pricing-templates/        - Create template
# GET    /api/vendor/pricing-templates/{id}/   - Get template
# PUT    /api/vendor/pricing-templates/{id}/   - Update template
# DELETE /api/vendor/pricing-templates/{id}/   - Delete template
# POST   /api/vendor/pricing-templates/{id}/apply/ - Apply template