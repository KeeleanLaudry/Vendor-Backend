from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS

from accounts.permissions import IsAdminJWT

from .models import (
    ServiceCategory,
    ItemType,
    AttributeType,
    AttributeOption
)

from .serializers import (
    ServiceCategorySerializer,
    ItemTypeSerializer,
    AttributeTypeSerializer,
    AttributeOptionSerializer
)


# ✅ SERVICE CATEGORY
class ServiceCategoryViewSet(viewsets.ModelViewSet):
    queryset = ServiceCategory.objects.filter(is_active=True)
    serializer_class = ServiceCategorySerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsAuthenticated()]   # ✅ vendor allowed (read only)
        return [IsAuthenticated(), IsAdminJWT()]  # ❌ write = admin only


# ✅ ITEM TYPE
class ItemTypeViewSet(viewsets.ModelViewSet):
    queryset = ItemType.objects.all()
    serializer_class = ItemTypeSerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsAuthenticated()]   # ✅ vendor allowed
        return [IsAuthenticated(), IsAdminJWT()]


# ✅ ATTRIBUTE TYPE
class AttributeTypeViewSet(viewsets.ModelViewSet):
    queryset = AttributeType.objects.all()
    serializer_class = AttributeTypeSerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsAuthenticated()]   # ✅ vendor allowed
        return [IsAuthenticated(), IsAdminJWT()]


# ✅ ATTRIBUTE OPTION
class AttributeOptionViewSet(viewsets.ModelViewSet):
    queryset = AttributeOption.objects.all()
    serializer_class = AttributeOptionSerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsAuthenticated()]   # ✅ vendor allowed
        return [IsAuthenticated(), IsAdminJWT()]