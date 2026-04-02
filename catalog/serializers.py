from rest_framework import serializers
from .models import (
    ServiceCategory,
    ItemType,
    AttributeType,
    AttributeOption,
    AddOn, FoldingOption, CustomisationOption,
    ItemAddOn, ItemFolding, ItemCustomisation

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

       


# ─── ADMIN: READ/WRITE ─────────────────────────────────────────────────────

class AddOnSerializer(serializers.ModelSerializer):
    class Meta:
        model  = AddOn
        fields = ['id', 'name', 'description',  'is_active']


class FoldingOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model  = FoldingOption
        fields = ['id', 'name', 'description',  'is_active']


class CustomisationOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model  = CustomisationOption
        fields = ['id', 'name', 'description',  'is_active']


# ─── VENDOR: ATTACH TO ITEM (read price but can't change it) ───────────────

class ItemAddOnSerializer(serializers.ModelSerializer):
    addon_name = serializers.CharField(source='addon.name', read_only=True)

    class Meta:
        model  = ItemAddOn
        fields = ['id', 'item_type', 'addon', 'addon_name']

class ItemFoldingSerializer(serializers.ModelSerializer):
    folding_name = serializers.CharField(source='folding_option.name', read_only=True)

    class Meta:
        model  = ItemFolding
        fields = ['id', 'item_type', 'folding_option', 'folding_name']


class ItemCustomisationSerializer(serializers.ModelSerializer):
    customisation_name = serializers.CharField(source='customisation_option.name', read_only=True)

    class Meta:
        model  = ItemCustomisation
        fields = ['id', 'item_type', 'customisation_option', 'customisation_name']

# ─── BONUS: Full item detail with all options embedded ─────────────────────

class ItemTypeDetailSerializer(serializers.ModelSerializer):
    addons                = ItemAddOnSerializer(many=True, read_only=True)
    folding_options       = ItemFoldingSerializer(many=True, read_only=True)
    customisation_options = ItemCustomisationSerializer(many=True, read_only=True)

    class Meta:
        model  = ItemType
        fields = ['id', 'name', 'addons', 'folding_options', 'customisation_options']