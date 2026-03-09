from django.contrib import admin
from .models import (
    ServiceCategory,
    ItemType,
    AttributeType,
    AttributeOption,
    VendorAttributeRequest
)


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug", "is_active", "created_at")
    search_fields = ("name",)
    list_filter = ("is_active",)


@admin.register(ItemType)
class ItemTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "is_active", "created_at")
    search_fields = ("name",)
    filter_horizontal = ("services",)


@admin.register(AttributeType)
class AttributeTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "is_required", "is_active", "created_at")
    filter_horizontal = ("applicable_services", "applicable_items")


@admin.register(AttributeOption)
class AttributeOptionAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "attribute_type", "is_active", "created_at")
    list_filter = ("attribute_type",)


@admin.register(VendorAttributeRequest)
class VendorAttributeRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "requested_value", "attribute_type", "vendor_id", "status")
    list_filter = ("status",)