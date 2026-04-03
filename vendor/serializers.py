from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from datetime import timedelta
import random

from .models import Vendor, VendorOTP, VendorProfile
from .utils import send_whatsapp_otp
from .models import VendorServicePricing
from catalog.models import (
   AttributeOption, AddOn, FoldingOption, CustomisationOption,
    ItemAddOn, ItemFolding, ItemCustomisation
)
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
        read_only_fields = ("vendor", "created_at")

    def update(self, instance, validated_data):
        # Only update fields that are actually sent
        for attr, value in validated_data.items():
            if value is not None:
                setattr(instance, attr, value)

        instance.save()
        return instance


class VendorServicePricingSerializer(serializers.ModelSerializer):
    attribute_options = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=AttributeOption.objects.all()
    )

    class Meta:
        model = VendorServicePricing
        fields = "__all__"
        read_only_fields = ["vendor_id"]

    def validate(self, attrs):
        request = self.context["request"]
        vendor_id = request.user.id

        service = attrs.get("service")
        item = attrs.get("item")
        attribute_options = attrs.get("attribute_options", [])

        # ✅ 1. Prevent duplicate combination
        existing = VendorServicePricing.objects.filter(
            vendor_id=vendor_id,
            service=service,
            item=item
        )

        for pricing in existing:
            existing_ids = set(pricing.attribute_options.values_list("id", flat=True))
            new_ids = set([opt.id for opt in attribute_options])

            if existing_ids == new_ids:
                raise serializers.ValidationError(
                    "This combination already exists"
                )

        # ✅ 2. Validate attribute belongs to item
        for option in attribute_options:
            attr_type = option.attribute_type

            if item.id not in attr_type.applicable_items.values_list("id", flat=True):
                raise serializers.ValidationError(
                    f"{option.name} is not valid for selected item"
                )

        # ✅ 3. Prevent multiple options of same attribute
        seen_types = set()

        for option in attribute_options:
            attr_type_id = option.attribute_type.id

            if attr_type_id in seen_types:
                raise serializers.ValidationError(
                    f"Multiple options selected for {option.attribute_type.name}"
                )

            seen_types.add(attr_type_id)

        return attrs
    
 

class ItemAddOnSerializer(serializers.ModelSerializer):
    addon_name  = serializers.CharField(source='addon.name', read_only=True)
    addon_price = serializers.DecimalField(source='addon.price', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model  = ItemAddOn
        fields = ['id', 'item_type', 'addon', 'addon_name', 'addon_price']

    def validate(self, attrs):
        request   = self.context['request']
        item_type = attrs.get('item_type')

        # Ensure vendor owns this item_type via their pricing
        if not VendorServicePricing.objects.filter(
            vendor_id=request.user.id,
            item=item_type
        ).exists():
            raise serializers.ValidationError("You don't have this item in your catalog")

        return attrs


class ItemFoldingSerializer(serializers.ModelSerializer):
    folding_name  = serializers.CharField(source='folding_option.name', read_only=True)
    folding_price = serializers.DecimalField(source='folding_option.price', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model  = ItemFolding
        fields = ['id', 'item_type', 'folding_option', 'folding_name', 'folding_price']

    def validate(self, attrs):
        request   = self.context['request']
        item_type = attrs.get('item_type')

        if not VendorServicePricing.objects.filter(
            vendor_id=request.user.id,
            item=item_type
        ).exists():
            raise serializers.ValidationError("You don't have this item in your catalog")

        return attrs


class ItemCustomisationSerializer(serializers.ModelSerializer):
    customisation_name  = serializers.CharField(source='customisation_option.name', read_only=True)
    customisation_price = serializers.DecimalField(source='customisation_option.price', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model  = ItemCustomisation
        fields = ['id', 'item_type', 'customisation_option', 'customisation_name', 'customisation_price']

    def validate(self, attrs):
        request   = self.context['request']
        item_type = attrs.get('item_type')

        if not VendorServicePricing.objects.filter(
            vendor_id=request.user.id,
            item=item_type
        ).exists():
            raise serializers.ValidationError("You don't have this item in your catalog")

        return attrs

