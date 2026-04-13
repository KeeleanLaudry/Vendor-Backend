from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ServiceCategoryViewSet,
    CategoryViewSet,  # ✨ NEW
    SubcategoryViewSet,  # ✨ NEW
    ItemTypeViewSet,
    AttributeTypeViewSet,
    AttributeOptionViewSet,
    DeliveryTierViewSet,  # ✨ NEW
    # Admin catalogue
    AddOnViewSet,
    FoldingOptionViewSet,
    CustomisationOptionViewSet,
    # Catalog tree
    CatalogTreeViewSet,  # ✨ NEW
)

router = DefaultRouter()

# ─── Core Catalog (Hierarchical Structure) ─────────────────────────────────
router.register("services", ServiceCategoryViewSet, basename="service")
router.register("categories", CategoryViewSet, basename="category")  # ✨ NEW
router.register("subcategories", SubcategoryViewSet, basename="subcategory")  # ✨ NEW
router.register("items", ItemTypeViewSet, basename="item")
router.register("delivery-tiers", DeliveryTierViewSet, basename="delivery-tier")  # ✨ NEW

# ─── Attributes ─────────────────────────────────────────────────────────────
router.register("attribute-types", AttributeTypeViewSet, basename="attribute-type")
router.register("attribute-options", AttributeOptionViewSet, basename="attribute-option")

# ─── Admin Catalogue Options ────────────────────────────────────────────────
# Admin creates these, vendors select from dropdowns when pricing
router.register("addons", AddOnViewSet, basename="addon")
router.register("folding-options", FoldingOptionViewSet, basename="folding-option")
router.register("customisation-options", CustomisationOptionViewSet, basename="customisation-option")

# ─── Catalog Tree ───────────────────────────────────────────────────────────
# Single endpoint to get all catalog data
router.register("tree", CatalogTreeViewSet, basename="catalog-tree")  # ✨ NEW

urlpatterns = [
    path("", include(router.urls)),
]


# ==================================================================================
# ❌ REMOVED ENDPOINTS
# ==================================================================================
# These have been removed as vendors now manage pricing through vendors app:
# - "item-addons" → Now in vendors/urls.py as part of VendorPrice
# - "item-foldings" → Now in vendors/urls.py as part of VendorPrice
# - "item-customisations" → Now in vendors/urls.py as part of VendorPrice
# ==================================================================================


# ==================================================================================
# 📋 AVAILABLE CATALOG ENDPOINTS
# ==================================================================================
# 
# GET /api/catalog/services/
#   → List all services (Dry Cleaning, Wash & Fold, Ironing)
# 
# GET /api/catalog/categories/
#   → List all categories (Male, Female, Kids)
# 
# GET /api/catalog/categories/by-service/?service_id=1
#   → List categories filtered by service
# 
# GET /api/catalog/subcategories/
#   → List all subcategories
# 
# GET /api/catalog/subcategories/by-category/?category_id=1
#   → List subcategories filtered by category
# 
# GET /api/catalog/subcategories/by-service-category/?service_id=1&category_id=2
#   → List subcategories filtered by BOTH service AND category
# 
# GET /api/catalog/items/
#   → List all items
# 
# GET /api/catalog/items/?service_id=1&category_id=2&subcategory_id=3
#   → List items filtered by any combination
# 
# GET /api/catalog/items/filtered/?service_id=1&category_id=2&subcategory_id=3
#   → List items matching ALL filters (complete permutation)
# 
# GET /api/catalog/delivery-tiers/
#   → List all delivery tiers (Standard, Express 2hr, etc.)
# 
# GET /api/catalog/attribute-types/
#   → List all attribute types (Fabric, Gender, etc.)
# 
# GET /api/catalog/attribute-options/?attribute_type_id=1
#   → List options for a specific attribute type
# 
# GET /api/catalog/addons/
#   → List all add-ons (Express, Gift Wrap, etc.)
# 
# GET /api/catalog/folding-options/
#   → List all folding options (Single Fold, Hanging, etc.)
# 
# GET /api/catalog/customisation-options/
#   → List all customisation options (Monogram, Embroidery, etc.)
# 
# GET /api/catalog/tree/
#   → Get ALL catalog data in one call (for vendor portal initialization)
#     Returns: services, categories, subcategories, items, attributes,
#              delivery_tiers, addons, folding_options, customisation_options
# 
# ==================================================================================