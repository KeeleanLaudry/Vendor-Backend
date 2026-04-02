from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS

from accounts.permissions import IsAdminJWT

from .models import (
    ServiceCategory,
    ItemType,
    AttributeType,
    AttributeOption,
  
    AddOn, FoldingOption, CustomisationOption,
    ItemAddOn, ItemFolding, ItemCustomisation
)


from .serializers import (
    ServiceCategorySerializer,
    ItemTypeSerializer,
    AttributeTypeSerializer,
    AttributeOptionSerializer,
   
    AddOnSerializer, FoldingOptionSerializer, CustomisationOptionSerializer,
    ItemAddOnSerializer, ItemFoldingSerializer, ItemCustomisationSerializer,
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



# ─── ADMIN ONLY: create the catalogue ─────────────────────────────────────

class AddOnViewSet(viewsets.ModelViewSet):
    queryset          = AddOn.objects.filter(is_active=True)
    serializer_class  = AddOnSerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsAuthenticated()]       # vendor can browse
        return [IsAuthenticated(), IsAdminJWT()]  # admin writes


class FoldingOptionViewSet(viewsets.ModelViewSet):
    queryset          = FoldingOption.objects.filter(is_active=True)
    serializer_class  = FoldingOptionSerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdminJWT()]


class CustomisationOptionViewSet(viewsets.ModelViewSet):
    queryset          = CustomisationOption.objects.filter(is_active=True)
    serializer_class  = CustomisationOptionSerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdminJWT()]


# ─── VENDOR: attach options to their items ─────────────────────────────────

class ItemAddOnViewSet(viewsets.ModelViewSet):
    serializer_class = ItemAddOnSerializer

    def get_permissions(self):
        return [IsAuthenticated()]   # vendor only, no admin check needed

    def get_queryset(self):
        qs = ItemAddOn.objects.select_related('addon', 'item_type')
        item_type = self.request.query_params.get('item_type')
        if item_type:
            qs = qs.filter(item_type_id=item_type)
        return qs


class ItemFoldingViewSet(viewsets.ModelViewSet):
    serializer_class = ItemFoldingSerializer

    def get_permissions(self):
        return [IsAuthenticated()]

    def get_queryset(self):
        qs = ItemFolding.objects.select_related('folding_option', 'item_type')
        item_type = self.request.query_params.get('item_type')
        if item_type:
            qs = qs.filter(item_type_id=item_type)
        return qs


class ItemCustomisationViewSet(viewsets.ModelViewSet):
    serializer_class = ItemCustomisationSerializer

    def get_permissions(self):
        return [IsAuthenticated()]

    def get_queryset(self):
        qs = ItemCustomisation.objects.select_related('customisation_option', 'item_type')
        item_type = self.request.query_params.get('item_type')
        if item_type:
            qs = qs.filter(item_type_id=item_type)
        return qs