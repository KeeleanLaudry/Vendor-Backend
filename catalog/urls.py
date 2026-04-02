from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ServiceCategoryViewSet,
    ItemTypeViewSet,
    AttributeTypeViewSet,
    AttributeOptionViewSet,
    # Admin catalogue
    AddOnViewSet,
    FoldingOptionViewSet,
    CustomisationOptionViewSet,
    # Vendor item linking
    ItemAddOnViewSet,
    ItemFoldingViewSet,
    ItemCustomisationViewSet,
)

router = DefaultRouter()

# ─── Existing ───────────────────────────────────────────
router.register("services",           ServiceCategoryViewSet)
router.register("items",              ItemTypeViewSet)
router.register("attribute-types",    AttributeTypeViewSet)
router.register("attribute-options",  AttributeOptionViewSet)

# ─── Admin catalogue (admin creates, vendor reads) ───────
router.register("addons",                   AddOnViewSet,               basename="addon")
router.register("folding-options",          FoldingOptionViewSet,        basename="folding-option")
router.register("customisation-options",    CustomisationOptionViewSet,  basename="customisation-option")

# ─── Vendor linking (vendor attaches options to their items) ─
router.register("item-addons",          ItemAddOnViewSet,       basename="item-addon")
router.register("item-foldings",        ItemFoldingViewSet,     basename="item-folding")
router.register("item-customisations",  ItemCustomisationViewSet, basename="item-customisation")

urlpatterns = [
    path("", include(router.urls)),
]