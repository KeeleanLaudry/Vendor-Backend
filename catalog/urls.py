from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ServiceCategoryViewSet,
    ItemTypeViewSet,
    AttributeTypeViewSet,
    AttributeOptionViewSet
)

router = DefaultRouter()

router.register("services", ServiceCategoryViewSet)
router.register("items", ItemTypeViewSet)
router.register("attribute-types", AttributeTypeViewSet)
router.register("attribute-options", AttributeOptionViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

