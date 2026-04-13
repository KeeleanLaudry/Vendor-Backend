from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from django.core.cache import cache

from accounts.permissions import IsAdminJWT

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
# ✅ SERVICE CATEGORY
# ==============================
class ServiceCategoryViewSet(viewsets.ModelViewSet):
    queryset = ServiceCategory.objects.filter(is_active=True)
    serializer_class = ServiceCategorySerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdminJWT()]


# ==============================
# ✅ CATEGORY (FIXED)
# ==============================
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer  # ✨ FIXED: Use full serializer
    
    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdminJWT()]
    
    @action(detail=False, methods=['get'], url_path='by-service')
    def by_service(self, request):
        """
        GET /api/catalog/categories/by-service/?service_id=1
        Returns categories filtered by service
        """
        service_id = request.query_params.get('service_id')
        if not service_id:
            return Response(
                {'error': 'service_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cache_key = f'categories_by_service_{service_id}'
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)
        
        categories = self.queryset.filter(services__id=service_id).distinct()
        serializer = CategorySerializer(categories, many=True)  # ✨ FIXED
        cache.set(cache_key, serializer.data, 3600)
        return Response(serializer.data)


# ==============================
# ✅ SUBCATEGORY (FIXED)
# ==============================
class SubcategoryViewSet(viewsets.ModelViewSet):
    queryset = Subcategory.objects.filter(is_active=True).select_related('category')
    serializer_class = SubcategorySerializer  # ✨ FIXED: Use full serializer
    
    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdminJWT()]
    
    @action(detail=False, methods=['get'], url_path='by-category')
    def by_category(self, request):
        """
        GET /api/catalog/subcategories/by-category/?category_id=1
        Returns subcategories filtered by category
        """
        category_id = request.query_params.get('category_id')
        if not category_id:
            return Response(
                {'error': 'category_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cache_key = f'subcategories_by_category_{category_id}'
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)
        
        subcategories = self.queryset.filter(category_id=category_id)
        serializer = SubcategorySerializer(subcategories, many=True)  # ✨ FIXED
        cache.set(cache_key, serializer.data, 3600)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='by-service-category')
    def by_service_category(self, request):
        """
        GET /api/catalog/subcategories/by-service-category/?service_id=1&category_id=2
        Returns subcategories filtered by service AND category
        """
        service_id = request.query_params.get('service_id')
        category_id = request.query_params.get('category_id')
        
        if not service_id or not category_id:
            return Response(
                {'error': 'Both service_id and category_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cache_key = f'subcategories_s{service_id}_c{category_id}'
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)
        
        subcategories = self.queryset.filter(
            category_id=category_id,
            services__id=service_id
        ).distinct()
        
        serializer = SubcategorySerializer(subcategories, many=True)  # ✨ FIXED
        cache.set(cache_key, serializer.data, 3600)
        return Response(serializer.data)


# ==============================
# ✅ ITEM TYPE (FIXED)
# ==============================
class ItemTypeViewSet(viewsets.ModelViewSet):
    queryset = ItemType.objects.filter(is_active=True)
    serializer_class = ItemTypeSerializer  # ✨ FIXED: Use full serializer as default
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ItemTypeDetailSerializer  # Single item detail
        return ItemTypeSerializer  # ✨ FIXED: List and create use full serializer
    
    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdminJWT()]
    
    def get_queryset(self):
        """
        Filter items by service, category, and/or subcategory
        GET /api/catalog/items/?service_id=1&category_id=2&subcategory_id=3
        """
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
    
    @action(detail=False, methods=['get'], url_path='filtered')
    def filtered(self, request):
        """
        GET /api/catalog/items/filtered/?service_id=1&category_id=2&subcategory_id=3
        Returns items matching ALL filters (complete permutation)
        """
        service_id = request.query_params.get('service_id')
        category_id = request.query_params.get('category_id')
        subcategory_id = request.query_params.get('subcategory_id')
        
        if not all([service_id, category_id, subcategory_id]):
            return Response(
                {'error': 'service_id, category_id, and subcategory_id are all required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cache_key = f'items_s{service_id}_c{category_id}_sc{subcategory_id}'
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)
        
        items = self.queryset.filter(
            services__id=service_id,
            categories__id=category_id,
            subcategories__id=subcategory_id
        ).distinct()
        
        serializer = ItemTypeSerializer(items, many=True)  # ✨ FIXED
        cache.set(cache_key, serializer.data, 3600)
        return Response(serializer.data)


# ==============================
# ✅ ATTRIBUTE TYPE (FIXED)
# ==============================
class AttributeTypeViewSet(viewsets.ModelViewSet):
    queryset = AttributeType.objects.filter(is_active=True)
    serializer_class = AttributeTypeSerializer  # ✨ FIXED: Use full serializer
    
    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdminJWT()]


# ==============================
# ✅ ATTRIBUTE OPTION
# ==============================
class AttributeOptionViewSet(viewsets.ModelViewSet):
    queryset = AttributeOption.objects.filter(is_active=True)
    serializer_class = AttributeOptionSerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdminJWT()]
    
    def get_queryset(self):
        """Filter by attribute_type if provided"""
        queryset = super().get_queryset()
        attribute_type_id = self.request.query_params.get('attribute_type_id')
        if attribute_type_id:
            queryset = queryset.filter(attribute_type_id=attribute_type_id)
        return queryset


# ==============================
# ✅ DELIVERY TIER
# ==============================
class DeliveryTierViewSet(viewsets.ModelViewSet):
    queryset = DeliveryTier.objects.filter(is_active=True)
    serializer_class = DeliveryTierSerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdminJWT()]


# ==============================
# ✅ ADD-ON
# ==============================
class AddOnViewSet(viewsets.ModelViewSet):
    queryset = AddOn.objects.filter(is_active=True)
    serializer_class = AddOnSerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdminJWT()]


# ==============================
# ✅ FOLDING OPTION
# ==============================
class FoldingOptionViewSet(viewsets.ModelViewSet):
    queryset = FoldingOption.objects.filter(is_active=True)
    serializer_class = FoldingOptionSerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdminJWT()]


# ==============================
# ✅ CUSTOMISATION OPTION
# ==============================
class CustomisationOptionViewSet(viewsets.ModelViewSet):
    queryset = CustomisationOption.objects.filter(is_active=True)
    serializer_class = CustomisationOptionSerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdminJWT()]


# ==============================
# ✅ CATALOG TREE
# ==============================
class CatalogTreeViewSet(viewsets.ViewSet):
    """
    Returns complete catalog in one API call
    Used by vendor portal to populate all dropdowns
    """
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """
        GET /api/catalog/tree/
        Returns all active catalog data for vendor portal
        """
        cache_key = 'catalog_tree_v1'
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)
        
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
        response_data = serializer.data
        
        cache.set(cache_key, response_data, 3600)
        return Response(response_data)