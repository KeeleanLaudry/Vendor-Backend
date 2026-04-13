from rest_framework.decorators import api_view, parser_classes, permission_classes, action
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db import transaction
from django.db.models import Q

from .serializers import (
    RequestOTPSerializer,
    VerifyOTPSerializer,
    VendorProfileSerializer,
    VendorPriceListSerializer,  # ✨ NEW
    VendorPriceCreateSerializer,  # ✨ NEW
    BulkVendorPriceSerializer,  # ✨ NEW
    VendorPriceAuditSerializer,  # ✨ NEW
    VendorPriceAttributeSerializer,  # ✨ NEW
    VendorPriceAddOnSerializer,  # ✨ NEW
    VendorPriceFoldingSerializer,  # ✨ NEW
    VendorPriceCustomisationSerializer,  # ✨ NEW
)

from .models import (
    VendorProfile,
    VendorPrice,  # ✨ NEW
    VendorPriceAttribute,  # ✨ NEW
    VendorPriceAddOn,  # ✨ NEW
    VendorPriceFolding,  # ✨ NEW
    VendorPriceCustomisation,  # ✨ NEW
    VendorPriceAudit,  # ✨ NEW
)

from catalog.models import (
    ServiceCategory,
    Category,
    Subcategory,
    ItemType,
)


# ==================================================================================
# AUTHENTICATION VIEWS
# ==================================================================================
# ✅ UNCHANGED - Kept as is

# --------------------------------
# REQUEST OTP
# --------------------------------
@api_view(['POST'])
@permission_classes([AllowAny])
def request_otp(request):
    serializer = RequestOTPSerializer(data=request.data)
    if serializer.is_valid():
        data = serializer.save()
        return Response({
            "message": "OTP sent",
            "vendor_id": data["vendor_id"]
        })
    return Response(serializer.errors, status=400)


# --------------------------------
# VERIFY OTP (JWT)
# --------------------------------
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp(request):
    serializer = VerifyOTPSerializer(data=request.data)
    if serializer.is_valid():
        return Response(serializer.save())
    return Response(serializer.errors, status=400)


# --------------------------------
# UPLOAD PROFILE (JWT Protected)
# --------------------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_profile(request):
    vendor = request.user

    profile, created = VendorProfile.objects.get_or_create(vendor=vendor)

    # Remove empty values
    data = request.data.copy()

    for key, value in list(data.items()):
        if value in ["", None]:
            data.pop(key)

    serializer = VendorProfileSerializer(
        profile,
        data=data,
        partial=True
    )

    if serializer.is_valid():
        serializer.save()

        # ✅ Mark profile as completed AFTER successful save
        profile.is_profile_completed = True
        profile.save(update_fields=["is_profile_completed"])

        return Response({
            "message": "Profile saved successfully",
            "created": created,
            "profile_completed": True
        })

    return Response(serializer.errors, status=400)


# --------------------------------
# GET PROFILE (JWT Protected)
# --------------------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_vendor_profile(request):
    vendor = request.user

    # Always create if not exists
    profile, created = VendorProfile.objects.get_or_create(vendor=vendor)

    serializer = VendorProfileSerializer(profile)
    return Response({
        "profile": serializer.data,
        "is_new": created
    })


# ==================================================================================
# 🔄 REFACTORED: VENDOR PRICING VIEWS
# ==================================================================================


# --------------------------------
# Vendor Price ViewSet
# --------------------------------
class VendorPriceViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for vendor pricing
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return VendorPriceCreateSerializer
        return VendorPriceListSerializer
    
    def get_queryset(self):
        """
        Returns prices for authenticated vendor only
        Supports filtering by service, category, subcategory, item
        """
        queryset = VendorPrice.objects.filter(
            vendor=self.request.user
        ).select_related(
            'service', 'category', 'subcategory', 'item', 'delivery_tier'
        ).prefetch_related(
            'attribute_selections',
            'attribute_selections__attribute_option',
            'addon_options',
            'addon_options__addon',
            'folding_options',
            'folding_options__folding_option',
            'customisation_options',
            'customisation_options__customisation_option',
        ).order_by('-updated_at')
        
        # Optional filters
        service_id = self.request.query_params.get('service_id')
        category_id = self.request.query_params.get('category_id')
        subcategory_id = self.request.query_params.get('subcategory_id')
        item_id = self.request.query_params.get('item_id')
        delivery_tier_id = self.request.query_params.get('delivery_tier_id')
        
        if service_id:
            queryset = queryset.filter(service_id=service_id)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if subcategory_id:
            queryset = queryset.filter(subcategory_id=subcategory_id)
        if item_id:
            queryset = queryset.filter(item_id=item_id)
        if delivery_tier_id:
            queryset = queryset.filter(delivery_tier_id=delivery_tier_id)
        
        return queryset
    
    def perform_create(self, serializer):
        """Auto-set vendor from authenticated user"""
        serializer.save()
    
    def perform_update(self, serializer):
        """Auto-set vendor from authenticated user"""
        serializer.save()
    
    @action(detail=False, methods=['post'], url_path='bulk-create')
    def bulk_create(self, request):
        """
        POST /api/vendors/prices/bulk-create/
        Bulk create/update vendor prices (max 500 at once)
        """
        serializer = BulkVendorPriceSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        created_count = 0
        updated_count = 0
        errors = []
        
        with transaction.atomic():
            for idx, price_data in enumerate(serializer.validated_data['prices']):
                try:
                    # Check if combination exists
                    existing = VendorPrice.objects.filter(
                        vendor=request.user,
                        service=price_data['service'],
                        category=price_data['category'],
                        subcategory=price_data['subcategory'],
                        item=price_data['item'],
                        delivery_tier=price_data.get('delivery_tier')
                    ).first()
                    
                    if existing:
                        # Update existing
                        for key, value in price_data.items():
                            if key not in ['attributes', 'addons', 'foldings', 'customisations']:
                                setattr(existing, key, value)
                        existing.save()
                        updated_count += 1
                    else:
                        # Create new
                        price_serializer = VendorPriceCreateSerializer(
                            data=price_data,
                            context={'request': request}
                        )
                        if price_serializer.is_valid():
                            price_serializer.save()
                            created_count += 1
                        else:
                            errors.append({
                                'index': idx,
                                'errors': price_serializer.errors
                            })
                
                except Exception as e:
                    errors.append({
                        'index': idx,
                        'error': str(e)
                    })
        
        return Response({
            'created': created_count,
            'updated': updated_count,
            'errors': errors
        }, status=status.HTTP_200_OK if not errors else status.HTTP_207_MULTI_STATUS)
    
    @action(detail=False, methods=['get'], url_path='missing-combinations')
    def missing_combinations(self, request):
        """
        GET /api/vendors/prices/missing-combinations/
        Returns possible combinations that vendor hasn't priced yet
        """
        vendor = request.user
        
        # Get all priced combinations
        priced_combos = set(
            VendorPrice.objects.filter(vendor=vendor).values_list(
                'service_id', 'category_id', 'subcategory_id', 'item_id', 'delivery_tier_id'
            )
        )
        
        # Generate all possible combinations from catalog
        missing = []
        items = ItemType.objects.filter(is_active=True).prefetch_related(
            'services', 'categories', 'subcategories'
        )
        
        for item in items:
            for service in item.services.filter(is_active=True):
                for category in item.categories.filter(is_active=True):
                    for subcategory in item.subcategories.filter(
                        is_active=True,
                        category=category
                    ):
                        # Standard tier (None)
                        combo = (service.id, category.id, subcategory.id, item.id, None)
                        if combo not in priced_combos:
                            missing.append({
                                'service_id': service.id,
                                'service_name': service.name,
                                'category_id': category.id,
                                'category_name': category.name,
                                'subcategory_id': subcategory.id,
                                'subcategory_name': subcategory.name,
                                'item_id': item.id,
                                'item_name': item.name,
                                'delivery_tier_id': None,
                                'delivery_tier_name': 'Standard'
                            })
        
        return Response({
            'count': len(missing),
            'combinations': missing[:100]  # Limit to 100 for performance
        })
    
    @action(detail=False, methods=['get'], url_path='audit-log')
    def audit_log(self, request):
        """
        GET /api/vendors/prices/audit-log/
        Returns price change history for vendor
        """
        audit_logs = VendorPriceAudit.objects.filter(
            vendor_price__vendor=request.user
        ).select_related(
            'vendor_price__service',
            'vendor_price__item',
            'changed_by'
        ).order_by('-changed_at')[:100]  # Last 100 changes
        
        serializer = VendorPriceAuditSerializer(audit_logs, many=True)
        return Response(serializer.data)


# --------------------------------
# Vendor Price - Manage Attributes
# --------------------------------
class VendorPriceAttributeViewSet(viewsets.ModelViewSet):
    """
    Manage attribute options for a vendor price
    """
    serializer_class = VendorPriceAttributeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Only show attributes for vendor's own prices"""
        vendor_price_id = self.request.query_params.get('vendor_price_id')
        
        queryset = VendorPriceAttribute.objects.filter(
            vendor_price__vendor=self.request.user
        ).select_related(
            'attribute_option',
            'attribute_option__attribute_type'
        )
        
        if vendor_price_id:
            queryset = queryset.filter(vendor_price_id=vendor_price_id)
        
        return queryset


# --------------------------------
# Vendor Price - Manage Add-Ons
# --------------------------------
class VendorPriceAddOnViewSet(viewsets.ModelViewSet):
    """
    Manage add-ons for a vendor price
    """
    serializer_class = VendorPriceAddOnSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Only show add-ons for vendor's own prices"""
        vendor_price_id = self.request.query_params.get('vendor_price_id')
        
        queryset = VendorPriceAddOn.objects.filter(
            vendor_price__vendor=self.request.user
        ).select_related('addon')
        
        if vendor_price_id:
            queryset = queryset.filter(vendor_price_id=vendor_price_id)
        
        return queryset


# --------------------------------
# Vendor Price - Manage Folding
# --------------------------------
class VendorPriceFoldingViewSet(viewsets.ModelViewSet):
    """
    Manage folding options for a vendor price
    """
    serializer_class = VendorPriceFoldingSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Only show folding for vendor's own prices"""
        vendor_price_id = self.request.query_params.get('vendor_price_id')
        
        queryset = VendorPriceFolding.objects.filter(
            vendor_price__vendor=self.request.user
        ).select_related('folding_option')
        
        if vendor_price_id:
            queryset = queryset.filter(vendor_price_id=vendor_price_id)
        
        return queryset


# --------------------------------
# Vendor Price - Manage Customisation
# --------------------------------
class VendorPriceCustomisationViewSet(viewsets.ModelViewSet):
    """
    Manage customisation options for a vendor price
    """
    serializer_class = VendorPriceCustomisationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Only show customisations for vendor's own prices"""
        vendor_price_id = self.request.query_params.get('vendor_price_id')
        
        queryset = VendorPriceCustomisation.objects.filter(
            vendor_price__vendor=self.request.user
        ).select_related('customisation_option')
        
        if vendor_price_id:
            queryset = queryset.filter(vendor_price_id=vendor_price_id)
        
        return queryset


# ==================================================================================
# ❌ REMOVED VIEWSETS
# ==================================================================================
# These have been replaced by the new pricing structure:
# - VendorServicePricingViewSet → Replaced by VendorPriceViewSet
# - VendorItemAddOnViewSet → Replaced by VendorPriceAddOnViewSet
# - VendorItemFoldingViewSet → Replaced by VendorPriceFoldingViewSet
# - VendorItemCustomisationViewSet → Replaced by VendorPriceCustomisationViewSet
# ==================================================================================