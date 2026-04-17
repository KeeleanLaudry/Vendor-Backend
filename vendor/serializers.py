# vendor/serializers.py

from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from datetime import timedelta
import random

from .models import (
    Vendor,
    VendorOTP,
    VendorProfile,
    VendorPrice,
    VendorPriceAttribute,
    VendorPriceAddOn,
    VendorPriceFolding,
    VendorPriceCustomisation,
    VendorPriceAudit,
    VendorPricing,
    VendorPricingTemplate,
    VendorPricingTemplateItem
)

from catalog.models import (
    ServiceCategory,
    Category,
    Subcategory,
    ItemType,
    AttributeOption,
    DeliveryTier,
    AddOn,
    FoldingOption,
    CustomisationOption,
)

from .utils import send_whatsapp_otp


# ==================================================================================
# AUTHENTICATION SERIALIZERS
# ==================================================================================

class RequestOTPSerializer(serializers.Serializer):
    phone = serializers.CharField(required=True)

    def validate(self, data):
        phone = data.get("phone")

        if not phone:
            raise serializers.ValidationError("Phone is required")

        phone = phone.strip()

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

    def create(self, validated_data):  # ✅ Correctly indented inside the class
        vendor = validated_data["vendor"]

        refresh = RefreshToken.for_user(vendor)

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


# ==================================================================================
# PROFILE SERIALIZER
# ==================================================================================

class VendorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorProfile
        fields = "__all__"
        read_only_fields = ("vendor", "created_at", "updated_at")

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if value is not None:
                setattr(instance, attr, value)
        instance.save()
        return instance


# ==================================================================================
# VENDOR PRICING SERIALIZERS
# ==================================================================================

class VendorPricingSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source='service.name', read_only=True, allow_null=True)
    category_name = serializers.CharField(source='category.name', read_only=True, allow_null=True)
    subcategory_name = serializers.CharField(source='subcategory.name', read_only=True, allow_null=True)
    item_name = serializers.CharField(source='item.name', read_only=True, allow_null=True)

    service_id = serializers.PrimaryKeyRelatedField(
        queryset=ServiceCategory.objects.all(),
        source='service',
        required=False,
        allow_null=True
    )
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        required=False,
        allow_null=True
    )
    subcategory_id = serializers.PrimaryKeyRelatedField(
        queryset=Subcategory.objects.all(),
        source='subcategory',
        required=False,
        allow_null=True
    )
    item_id = serializers.PrimaryKeyRelatedField(
        queryset=ItemType.objects.all(),
        source='item',
        required=False,
        allow_null=True
    )

    class Meta:
        model = VendorPricing
        fields = [
            'id',
            'vendor',
            'service_id', 'service_name',
            'category_id', 'category_name',
            'subcategory_id', 'subcategory_name',
            'item_id', 'item_name',
            'base_price',
            'pricing_level',
            'is_active',
            'notes',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'vendor', 'pricing_level', 'created_at', 'updated_at']

    def validate(self, data):
        has_service = data.get('service') is not None
        has_category = data.get('category') is not None
        has_subcategory = data.get('subcategory') is not None

        if has_category and not has_service:
            raise serializers.ValidationError({
                'category': 'Cannot set category without selecting a service'
            })

        if has_subcategory and not has_category:
            raise serializers.ValidationError({
                'subcategory': 'Cannot set subcategory without selecting a category'
            })

        return data


class VendorPricingBulkCreateSerializer(serializers.Serializer):
    service_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False, allow_empty=True
    )
    category_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False, allow_empty=True
    )
    subcategory_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False, allow_empty=True
    )
    item_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False, allow_empty=True
    )
    base_price = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate_base_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0")
        return value


class VendorPricingCSVSerializer(serializers.Serializer):
    service = serializers.CharField(allow_blank=True)
    category = serializers.CharField(allow_blank=True)
    subcategory = serializers.CharField(allow_blank=True)
    item = serializers.CharField(allow_blank=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2)


class VendorPricingStatsSerializer(serializers.Serializer):
    total_rules = serializers.IntegerField()
    coverage_percentage = serializers.FloatField()
    missing_items_count = serializers.IntegerField()
    pricing_by_level = serializers.DictField()
    average_price = serializers.DecimalField(max_digits=10, decimal_places=2)


class VendorPricingTemplateSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()

    class Meta:
        model = VendorPricingTemplate
        fields = ['id', 'name', 'description', 'items', 'created_at']

    def get_items(self, obj):
        return [{
            'service_id': item.service_id,
            'category_id': item.category_id,
            'subcategory_id': item.subcategory_id,
            'item_id': item.item_id,
            'base_price': item.base_price
        } for item in obj.items.all()]