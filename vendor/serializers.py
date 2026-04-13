from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from datetime import timedelta
import random

from .models import (
    Vendor,
    VendorOTP,
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
    Category,  # ✨ NEW
    Subcategory,  # ✨ NEW
    ItemType,
    AttributeOption,
    DeliveryTier,  # ✨ NEW
    AddOn,
    FoldingOption,
    CustomisationOption,
)

from .utils import send_whatsapp_otp


# ==================================================================================
# AUTHENTICATION SERIALIZERS
# ==================================================================================
# ✅ UNCHANGED - Kept as is

# ---------------------------------------------------------
class RequestOTPSerializer(serializers.Serializer):
    phone = serializers.CharField(required=True)

    def validate(self, data):
        phone = data.get("phone")

        if not phone:
            raise serializers.ValidationError("Phone is required")

        phone = phone.strip()

        # Convert 05XXXXXXXX → 9715XXXXXXXX
        if phone.startswith("0"):
            phone = "971" + phone[1:]

        data["phone"] = phone
        return data

    def create(self, validated_data):
        phone = validated_data["phone"]

        vendor, created = Vendor.objects.get_or_create(phone=phone)

        otp = str(random.randint(100000, 999999))
        expiry = timezone.now() + timedelta(minutes=5)

        VendorOTP.objects.create(
            vendor=vendor,
            otp=otp,
            expiry=expiry
        )

        send_whatsapp_otp(phone, otp)

        return {"vendor_id": vendor.id}


class VerifyOTPSerializer(serializers.Serializer):
    phone = serializers.CharField(required=True)
    otp = serializers.CharField(required=True)

    def validate(self, data):
        phone = data.get("phone").strip()
        otp = data.get("otp")

        if phone.startswith("0"):
            phone = "971" + phone[1:]

        try:
            vendor = Vendor.objects.get(phone=phone)
        except Vendor.DoesNotExist:
            raise serializers.ValidationError("Vendor not found")

        otp_record = VendorOTP.objects.filter(vendor=vendor).order_by("-created_at").first()

        if not otp_record:
            raise serializers.ValidationError("OTP not found")

        if timezone.now() > otp_record.expiry:
            raise serializers.ValidationError("OTP expired")

        if otp_record.otp != otp:
            raise serializers.ValidationError("Invalid OTP")

        data["vendor"] = vendor
        return data

    def create(self, validated_data):
        vendor = validated_data["vendor"]

        refresh = RefreshToken.for_user(vendor)

        # Custom payload
        refresh["vendor_id"] = vendor.id
        refresh["role"] = vendor.role

        access = refresh.access_token
        access["vendor_id"] = vendor.id
        access["role"] = vendor.role

        return {
            "message": "OTP verified",
            "vendor_id": vendor.id,
            "role": vendor.role,
            "access": str(access),
            "refresh": str(refresh),
        }


class VendorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorProfile
        fields = "__all__"
        read_only_fields = ("vendor", "created_at", "updated_at")

    def update(self, instance, validated_data):
        # Only update fields that are actually sent
        for attr, value in validated_data.items():
            if value is not None:
                setattr(instance, attr, value)

        instance.save()
        return instance


# ==================================================================================
# 🔄 REFACTORED: VENDOR PRICING SERIALIZERS
# ==================================================================================


# ---------------------------------------------------------
# Nested Serializers for Read Operations
# ---------------------------------------------------------

class VendorPriceAttributeSerializer(serializers.ModelSerializer):
    """For nested display of attribute options"""
    attribute_type_name = serializers.CharField(source='attribute_option.attribute_type.name', read_only=True)
    attribute_option_name = serializers.CharField(source='attribute_option.name', read_only=True)
    effective_surcharge = serializers.SerializerMethodField()
    
    class Meta:
        model = VendorPriceAttribute
        fields = [
            'id', 'attribute_option', 'attribute_type_name', 'attribute_option_name',
            'custom_surcharge_pct', 'effective_surcharge'
        ]
    
    def get_effective_surcharge(self, obj):
        return obj.get_effective_surcharge()


class VendorPriceAddOnSerializer(serializers.ModelSerializer):
    """For nested display of add-ons"""
    addon_name = serializers.CharField(source='addon.name', read_only=True)
    
    class Meta:
        model = VendorPriceAddOn
        fields = ['id', 'addon', 'addon_name', 'addon_price']


class VendorPriceFoldingSerializer(serializers.ModelSerializer):
    """For nested display of folding options"""
    folding_name = serializers.CharField(source='folding_option.name', read_only=True)
    
    class Meta:
        model = VendorPriceFolding
        fields = ['id', 'folding_option', 'folding_name', 'folding_price']


class VendorPriceCustomisationSerializer(serializers.ModelSerializer):
    """For nested display of customisation options"""
    customisation_name = serializers.CharField(source='customisation_option.name', read_only=True)
    
    class Meta:
        model = VendorPriceCustomisation
        fields = ['id', 'customisation_option', 'customisation_name', 'customisation_price']


# ---------------------------------------------------------
# Main Vendor Price Serializer (Read)
# ---------------------------------------------------------

class VendorPriceListSerializer(serializers.ModelSerializer):
    """Detailed serializer for displaying vendor prices"""
    
    # Display names for catalog fields
    service_name = serializers.CharField(source='service.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    subcategory_name = serializers.CharField(source='subcategory.name', read_only=True)
    item_name = serializers.CharField(source='item.name', read_only=True)
    delivery_tier_name = serializers.CharField(source='delivery_tier.name', read_only=True, allow_null=True)
    
    # Nested relationships
    attribute_selections = VendorPriceAttributeSerializer(many=True, read_only=True)
    addon_options = VendorPriceAddOnSerializer(many=True, read_only=True)
    folding_options = VendorPriceFoldingSerializer(many=True, read_only=True)
    customisation_options = VendorPriceCustomisationSerializer(many=True, read_only=True)
    
    class Meta:
        model = VendorPrice
        fields = [
            'id', 'vendor',
            'service', 'service_name',
            'category', 'category_name',
            'subcategory', 'subcategory_name',
            'item', 'item_name',
            'delivery_tier', 'delivery_tier_name',
            'price', 'image', 'turnaround_time', 'is_active',
            'attribute_selections', 'addon_options', 
            'folding_options', 'customisation_options',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['vendor', 'created_at', 'updated_at']


# ---------------------------------------------------------
# Vendor Price Create/Update Serializer
# ---------------------------------------------------------

class VendorPriceCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating vendor prices"""
    
    # Optional nested creation
    attributes = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False,
        help_text="[{'attribute_option': 1, 'custom_surcharge_pct': 10}]"
    )
    
    addons = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False,
        help_text="[{'addon': 1, 'addon_price': 10.00}]"
    )
    
    foldings = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False,
        help_text="[{'folding_option': 1, 'folding_price': 5.00}]"
    )
    
    customisations = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False,
        help_text="[{'customisation_option': 1, 'customisation_price': 15.00}]"
    )
    
    class Meta:
        model = VendorPrice
        fields = [
            'service', 'category', 'subcategory', 'item',
            'delivery_tier', 'price', 'image', 'turnaround_time',
            'is_active', 'attributes', 'addons', 'foldings', 'customisations'
        ]
    
    def validate(self, attrs):
        """Validate the hierarchical structure"""
        service = attrs.get('service')
        category = attrs.get('category')
        subcategory = attrs.get('subcategory')
        item = attrs.get('item')
        
        # ✅ 1. Validate category supports service
        if not category.services.filter(id=service.id).exists():
            raise serializers.ValidationError(
                f"Category '{category.name}' does not support service '{service.name}'"
            )
        
        # ✅ 2. Validate subcategory belongs to category and supports service
        if subcategory.category != category:
            raise serializers.ValidationError(
                f"Subcategory '{subcategory.name}' does not belong to category '{category.name}'"
            )
        
        if not subcategory.services.filter(id=service.id).exists():
            raise serializers.ValidationError(
                f"Subcategory '{subcategory.name}' does not support service '{service.name}'"
            )
        
        # ✅ 3. Validate item supports service, category, and subcategory
        if not item.services.filter(id=service.id).exists():
            raise serializers.ValidationError(
                f"Item '{item.name}' does not support service '{service.name}'"
            )
        
        if not item.categories.filter(id=category.id).exists():
            raise serializers.ValidationError(
                f"Item '{item.name}' is not available in category '{category.name}'"
            )
        
        if not item.subcategories.filter(id=subcategory.id).exists():
            raise serializers.ValidationError(
                f"Item '{item.name}' is not available in subcategory '{subcategory.name}'"
            )
        
        return attrs
    
    def create(self, validated_data):
        """Create vendor price with nested relationships"""
        # Extract nested data
        attributes_data = validated_data.pop('attributes', [])
        addons_data = validated_data.pop('addons', [])
        foldings_data = validated_data.pop('foldings', [])
        customisations_data = validated_data.pop('customisations', [])
        
        # Get vendor from request context
        vendor = self.context['request'].user
        validated_data['vendor'] = vendor
        
        # Create main price record
        vendor_price = VendorPrice.objects.create(**validated_data)
        
        # Create nested relationships
        for attr_data in attributes_data:
            VendorPriceAttribute.objects.create(
                vendor_price=vendor_price,
                **attr_data
            )
        
        for addon_data in addons_data:
            VendorPriceAddOn.objects.create(
                vendor_price=vendor_price,
                **addon_data
            )
        
        for folding_data in foldings_data:
            VendorPriceFolding.objects.create(
                vendor_price=vendor_price,
                **folding_data
            )
        
        for customisation_data in customisations_data:
            VendorPriceCustomisation.objects.create(
                vendor_price=vendor_price,
                **customisation_data
            )
        
        return vendor_price
    
    def update(self, instance, validated_data):
        """Update vendor price (nested relationships must be updated separately)"""
        # Remove nested data (update them via separate endpoints)
        validated_data.pop('attributes', None)
        validated_data.pop('addons', None)
        validated_data.pop('foldings', None)
        validated_data.pop('customisations', None)
        
        # Update main fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance


# ---------------------------------------------------------
# Bulk Price Upload Serializer
# ---------------------------------------------------------

class BulkVendorPriceSerializer(serializers.Serializer):
    """For bulk price creation/update"""
    prices = VendorPriceCreateSerializer(many=True)
    
    def validate_prices(self, value):
        if not value:
            raise serializers.ValidationError("At least one price entry is required")
        if len(value) > 500:
            raise serializers.ValidationError("Maximum 500 prices can be uploaded at once")
        return value


# ---------------------------------------------------------
# Price Audit Serializer
# ---------------------------------------------------------

class VendorPriceAuditSerializer(serializers.ModelSerializer):
    """For displaying price change history"""
    vendor_name = serializers.CharField(source='vendor_price.vendor.company_name', read_only=True)
    item_name = serializers.CharField(source='vendor_price.item.name', read_only=True)
    service_name = serializers.CharField(source='vendor_price.service.name', read_only=True)
    changed_by_phone = serializers.CharField(source='changed_by.phone', read_only=True)
    
    class Meta:
        model = VendorPriceAudit
        fields = [
            'id', 'vendor_price', 'vendor_name', 'item_name', 'service_name',
            'old_price', 'new_price', 'changed_by', 'changed_by_phone', 'changed_at'
        ]


# ==================================================================================
# ❌ REMOVED SERIALIZERS
# ==================================================================================
# These have been removed as the models moved to new pricing structure:
# - VendorServicePricingSerializer → Replaced by VendorPriceCreateSerializer
# - ItemAddOnSerializer → Replaced by VendorPriceAddOnSerializer
# - ItemFoldingSerializer → Replaced by VendorPriceFoldingSerializer
# - ItemCustomisationSerializer → Replaced by VendorPriceCustomisationSerializer
# ==================================================================================