from rest_framework import serializers
from .models import (
    ServiceCategory,
    ItemType,
    AttributeType,
    AttributeOption
)


class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = "__all__"


class ItemTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemType
        fields = "__all__"


class AttributeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttributeType
        fields = "__all__"


class AttributeOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttributeOption
        fields = "__all__"