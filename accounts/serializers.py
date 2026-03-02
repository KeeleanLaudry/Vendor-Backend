from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .models import AdminUser


class AdminLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        try:
            admin = AdminUser.objects.get(email=email)
        except AdminUser.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials")

        if not admin.check_password(password):
            raise serializers.ValidationError("Invalid credentials")

        if not admin.is_active:
            raise serializers.ValidationError("Admin inactive")

        data["admin"] = admin
        return data

    def create(self, validated_data):
        admin = validated_data["admin"]

        refresh = RefreshToken()

        refresh["admin_id"] = admin.id
        refresh["role"] = "admin"

        access = refresh.access_token
        access["admin_id"] = admin.id
        access["role"] = "admin"

        return {
            "message": "Login successful",
            "admin_id": admin.id,
            "role": "admin",
            "access": str(access),
            "refresh": str(refresh),
        }