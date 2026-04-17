from rest_framework import serializers
from .models import (
    ServiceCategory,
    Category,
    Subcategory,
    ItemType,
    ItemService,
    ItemCategory,
    ItemSubcategory,
    AttributeType,
    AttributeOption,
    DeliveryTier,
    AddOn,
    FoldingOption,
    CustomisationOption,
)


# ==============================
# Service Category Serializer
# ==============================
class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = ['id', 'name', 'slug', 'description', 'is_active', 'created_at', 'updated_at']


# ==============================
# Category Serializers
# ==============================
class CategorySerializer(serializers.ModelSerializer):
    services = ServiceCategorySerializer(many=True, read_only=True)
    service_ids = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=ServiceCategory.objects.all(),
        source='services',
        write_only=True
    )
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'services', 'service_ids', 'is_active', 'created_at', 'updated_at']


class CategoryListSerializer(serializers.ModelSerializer):
    """Lightweight version for dropdowns"""
    services = ServiceCategorySerializer(many=True, read_only=True)  # ✅ ADD THIS LINE
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'is_active', 'services']  # ✅ ADD 'services' HERE
    
    def get_service_count(self, obj):
        return obj.services.filter(is_active=True).count()


# ==============================
# Subcategory Serializers
# ==============================
class SubcategorySerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    services = ServiceCategorySerializer(many=True, read_only=True)
    service_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=ServiceCategory.objects.all(),
        source='services',
        write_only=True
    )
    
    class Meta:
        model = Subcategory
        fields = [
            'id', 'name', 'category', 'category_name', 
            'services', 'service_ids', 'is_active', 
            'created_at', 'updated_at'
        ]


class SubcategoryListSerializer(serializers.ModelSerializer):
    """Lightweight version for dropdowns"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Subcategory
        fields = ['id', 'name', 'category', 'category_name', 'is_active']


# ==============================
# ✅ FIXED: Item Type Serializers
# ==============================
class ItemTypeSerializer(serializers.ModelSerializer):
    """Full detail serializer with WRITE support"""
    # READ fields
    services = ServiceCategorySerializer(many=True, read_only=True)
    categories = CategoryListSerializer(many=True, read_only=True)
    subcategories = SubcategoryListSerializer(many=True, read_only=True)
    
    # ✨ WRITE fields (NEW!)
    service_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=ServiceCategory.objects.all(),
        source='services',
        write_only=True,
        required=False
    )
    category_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Category.objects.all(),
        source='categories',
        write_only=True,
        required=False
    )
    subcategory_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Subcategory.objects.all(),
        source='subcategories',
        write_only=True,
        required=False
    )
    
    class Meta:
        model = ItemType
        fields = [
            'id', 'name', 'description', 'image_url',
            'services', 'categories', 'subcategories',
            'service_ids', 'category_ids', 'subcategory_ids',  # ✨ NEW
            'is_active', 'created_at', 'updated_at'
        ]


class ItemTypeListSerializer(serializers.ModelSerializer):
    """Lightweight version for dropdowns"""
    class Meta:
        model = ItemType
        fields = ['id', 'name', 'description', 'image_url', 'is_active']


class ItemTypeDetailSerializer(serializers.ModelSerializer):
    """
    Complete item detail with all relationships
    Used for vendor portal to show what combinations are possible
    """
    services = ServiceCategorySerializer(many=True, read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    subcategories = SubcategorySerializer(many=True, read_only=True)
    
    class Meta:
        model = ItemType
        fields = [
            'id', 'name', 'description', 'image_url',
            'services', 'categories', 'subcategories',
            'is_active', 'created_at', 'updated_at'
        ]


# ==============================
# Attribute Type & Option Serializers
# ==============================
class AttributeOptionSerializer(serializers.ModelSerializer):
    attribute_type_name = serializers.CharField(source='attribute_type.name', read_only=True)
    
    class Meta:
        model = AttributeOption
        fields = [
            'id', 'attribute_type', 'attribute_type_name', 'name',
            'surcharge_pct', 'is_active', 'created_at', 'updated_at'
        ]


class AttributeTypeSerializer(serializers.ModelSerializer):
    options = AttributeOptionSerializer(many=True, read_only=True)
    
    class Meta:
        model = AttributeType
        fields = [
            'id', 'name', 'display_label', 'input_type',
            'is_required', 'is_active', 'options',
            'created_at', 'updated_at'
        ]


class AttributeTypeListSerializer(serializers.ModelSerializer):
    """Lightweight version for dropdowns"""
    option_count = serializers.SerializerMethodField()
    
    class Meta:
        model = AttributeType
        fields = ['id', 'name', 'display_label', 'input_type', 'is_required', 'option_count']
    
    def get_option_count(self, obj):
        return obj.options.filter(is_active=True).count()


# ==============================
# Delivery Tier Serializer
# ==============================
class DeliveryTierSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryTier
        fields = [
            'id', 'name', 'hours_sla', 'surcharge_type',
            'default_surcharge', 'is_active',
            'created_at', 'updated_at'
        ]


# ==============================
# Add-On, Folding, Customisation Serializers
# ==============================
class AddOnSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddOn
        fields = ['id', 'name', 'description', 'is_active', 'created_at', 'updated_at']


class FoldingOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoldingOption
        fields = ['id', 'name', 'description', 'is_active', 'created_at', 'updated_at']


class CustomisationOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomisationOption
        fields = ['id', 'name', 'description', 'is_active', 'created_at', 'updated_at']


# ==============================
# Catalog Tree Serializer
# ==============================
class CatalogTreeSerializer(serializers.Serializer):
    """
    Returns complete catalog structure for vendor portal
    Vendor uses this to populate all dropdowns
    """
    services = ServiceCategorySerializer(many=True, read_only=True)
    categories = CategoryListSerializer(many=True, read_only=True)
    subcategories = SubcategoryListSerializer(many=True, read_only=True)
    items = ItemTypeListSerializer(many=True, read_only=True)
    attributes = AttributeTypeSerializer(many=True, read_only=True)
    delivery_tiers = DeliveryTierSerializer(many=True, read_only=True)
    addons = AddOnSerializer(many=True, read_only=True)
    folding_options = FoldingOptionSerializer(many=True, read_only=True)
    customisation_options = CustomisationOptionSerializer(many=True, read_only=True)


# ==============================
# Filtered Dropdown Serializers
# ==============================
class FilteredCategoriesSerializer(serializers.Serializer):
    """Get categories filtered by service"""
    service_id = serializers.IntegerField()
    categories = CategoryListSerializer(many=True, read_only=True)


class FilteredSubcategoriesSerializer(serializers.Serializer):
    """Get subcategories filtered by service + category"""
    service_id = serializers.IntegerField()
    category_id = serializers.IntegerField()
    subcategories = SubcategoryListSerializer(many=True, read_only=True)


class FilteredItemsSerializer(serializers.Serializer):
    """Get items filtered by service + category + subcategory"""
    service_id = serializers.IntegerField()
    category_id = serializers.IntegerField()
    subcategory_id = serializers.IntegerField()
    items = ItemTypeListSerializer(many=True, read_only=True)
