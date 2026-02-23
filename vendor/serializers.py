from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from datetime import timedelta
import random

from .models import Vendor, VendorOTP, VendorProfile
from .utils import send_whatsapp_otp


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