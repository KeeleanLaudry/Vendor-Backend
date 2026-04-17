# catalog/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import SAFE_METHODS
from django.core.cache import cache

# ✅ USE YOUR EXISTING PERMISSIONS
from accounts.permissions import IsAdminJWT
from vendor.permissions import IsVendorJWT

from .models import (
    ServiceCategory,
    Category,
    Subcategory,
    ItemType,
    AttributeType,
    AttributeOption,
    DeliveryTier,
    AddOn,
    FoldingOption,
    CustomisationOption,
)

from .serializers import (
    ServiceCategorySerializer,
    CategorySerializer,
    CategoryListSerializer,
    SubcategorySerializer,
    SubcategoryListSerializer,
    ItemTypeSerializer,
    ItemTypeListSerializer,
    ItemTypeDetailSerializer,
    AttributeTypeSerializer,
    AttributeTypeListSerializer,
    AttributeOptionSerializer,
    DeliveryTierSerializer,
    AddOnSerializer,
    FoldingOptionSerializer,
    CustomisationOptionSerializer,
    CatalogTreeSerializer,
)


# ==============================
# ✅ COMBINED PERMISSION
# ==============================
from rest_framework.permissions import BasePermission

class IsAdminOrVendor(BasePermission):
    """Allows both Admin and Vendor"""
    
    def has_permission(self, request, view):
        user = request.user
        
        if not user or not user.is_authenticated:
            return False
        
        # Check role attribute
        role = getattr(user, "role", None)
        
        # Allow admin or vendor
        return role in ["admin", "vendor"]


# ==============================
# VIEWSETS
# ==============================

class ServiceCategoryViewSet(viewsets.ModelViewSet):
    queryset = ServiceCategory.objects.filter(is_active=True)
    serializer_class = ServiceCategorySerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsAdminOrVendor()]
        return [IsAdminJWT()]


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.filter(is_active=True)
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CategoryListSerializer
        return CategorySerializer
    
    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsAdminOrVendor()]
        return [IsAdminJWT()]
    
    @action(detail=False, methods=['get'], url_path='by-service')
    def by_service(self, request):
        service_id = request.query_params.get('service_id')
        if not service_id:
            return Response({'error': 'service_id required'}, status=400)
        
        categories = self.queryset.filter(services__id=service_id).distinct()
        serializer = CategoryListSerializer(categories, many=True)
        return Response(serializer.data)


class SubcategoryViewSet(viewsets.ModelViewSet):
    queryset = Subcategory.objects.filter(is_active=True).select_related('category')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return SubcategoryListSerializer
        return SubcategorySerializer
    
    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsAdminOrVendor()]
        return [IsAdminJWT()]
    
    @action(detail=False, methods=['get'], url_path='by-category')
    def by_category(self, request):
        category_id = request.query_params.get('category_id')
        if not category_id:
            return Response({'error': 'category_id required'}, status=400)
        
        subcategories = self.queryset.filter(category_id=category_id)
        serializer = SubcategoryListSerializer(subcategories, many=True)
        return Response(serializer.data)


class ItemTypeViewSet(viewsets.ModelViewSet):
    queryset = ItemType.objects.filter(is_active=True)
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ItemTypeDetailSerializer
        elif self.action == 'list':
            return ItemTypeListSerializer
        return ItemTypeSerializer
    
    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsAdminOrVendor()]
        return [IsAdminJWT()]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        service_id = self.request.query_params.get('service_id')
        category_id = self.request.query_params.get('category_id')
        subcategory_id = self.request.query_params.get('subcategory_id')
        
        if service_id:
            queryset = queryset.filter(services__id=service_id)
        if category_id:
            queryset = queryset.filter(categories__id=category_id)
        if subcategory_id:
            queryset = queryset.filter(subcategories__id=subcategory_id)
        
        return queryset.distinct()


class AttributeTypeViewSet(viewsets.ModelViewSet):
    queryset = AttributeType.objects.filter(is_active=True)
    
    def get_serializer_class(self):
        if self.action == 'list':
            return AttributeTypeListSerializer
        return AttributeTypeSerializer
    
    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsAdminOrVendor()]
        return [IsAdminJWT()]


class AttributeOptionViewSet(viewsets.ModelViewSet):
    queryset = AttributeOption.objects.filter(is_active=True)
    serializer_class = AttributeOptionSerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsAdminOrVendor()]
        return [IsAdminJWT()]


class DeliveryTierViewSet(viewsets.ModelViewSet):
    queryset = DeliveryTier.objects.filter(is_active=True)
    serializer_class = DeliveryTierSerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsAdminOrVendor()]
        return [IsAdminJWT()]


class AddOnViewSet(viewsets.ModelViewSet):
    queryset = AddOn.objects.filter(is_active=True)
    serializer_class = AddOnSerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsAdminOrVendor()]
        return [IsAdminJWT()]


class FoldingOptionViewSet(viewsets.ModelViewSet):
    queryset = FoldingOption.objects.filter(is_active=True)
    serializer_class = FoldingOptionSerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsAdminOrVendor()]
        return [IsAdminJWT()]


class CustomisationOptionViewSet(viewsets.ModelViewSet):
    queryset = CustomisationOption.objects.filter(is_active=True)
    serializer_class = CustomisationOptionSerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsAdminOrVendor()]
        return [IsAdminJWT()]


class CatalogTreeViewSet(viewsets.ViewSet):
    permission_classes = [IsAdminOrVendor]
    
    def list(self, request):
        data = {
            'services': ServiceCategory.objects.filter(is_active=True),
            'categories': Category.objects.filter(is_active=True),
            'subcategories': Subcategory.objects.filter(is_active=True).select_related('category'),
            'items': ItemType.objects.filter(is_active=True),
            'attributes': AttributeType.objects.filter(is_active=True).prefetch_related('options'),
            'delivery_tiers': DeliveryTier.objects.filter(is_active=True),
            'addons': AddOn.objects.filter(is_active=True),
            'folding_options': FoldingOption.objects.filter(is_active=True),
            'customisation_options': CustomisationOption.objects.filter(is_active=True),
        }
        
        serializer = CatalogTreeSerializer(data)
        return Response(serializer.data)