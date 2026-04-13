from django.contrib import admin
from django.utils.html import format_html
from .models import (
    ServiceCategory,
    Category,  # ✨ NEW
    Subcategory,  # ✨ NEW
    ItemType,
    ItemService,  # ✨ NEW
    ItemCategory,  # ✨ NEW
    ItemSubcategory,  # ✨ NEW
    AttributeType,
    AttributeOption,
    DeliveryTier,  # ✨ NEW
    AddOn,
    FoldingOption,
    CustomisationOption,
)


# ==================================================================================
# SERVICE CATEGORY
# ==================================================================================
@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug", "is_active", "category_count", "created_at")
    search_fields = ("name", "slug")
    list_filter = ("is_active",)
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at")
    
    fieldsets = (
        ("Basic Information", {
            "fields": ("name", "slug", "description", "is_active")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    
    def category_count(self, obj):
        return obj.categories.count()
    category_count.short_description = "Categories"


# ==================================================================================
# ✨ NEW: CATEGORY
# ==================================================================================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "is_active", "services_display", "subcategory_count", "created_at")
    search_fields = ("name",)
    list_filter = ("is_active",)
    filter_horizontal = ("services",)
    readonly_fields = ("created_at", "updated_at")
    
    fieldsets = (
        ("Basic Information", {
            "fields": ("name", "is_active")
        }),
        ("Services", {
            "fields": ("services",),
            "description": "Select which services support this category"
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    
    def services_display(self, obj):
        services = obj.services.filter(is_active=True)
        if services:
            return ", ".join([s.name for s in services])
        return "-"
    services_display.short_description = "Services"
    
    def subcategory_count(self, obj):
        return obj.subcategories.count()
    subcategory_count.short_description = "Subcategories"


# ==================================================================================
# ✨ NEW: SUBCATEGORY
# ==================================================================================
@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category", "is_active", "services_display", "item_count", "created_at")
    search_fields = ("name", "category__name")
    list_filter = ("is_active", "category")
    filter_horizontal = ("services",)
    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ("category",)
    
    fieldsets = (
        ("Basic Information", {
            "fields": ("name", "category", "is_active")
        }),
        ("Services", {
            "fields": ("services",),
            "description": "Select which services support this subcategory"
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    
    def services_display(self, obj):
        services = obj.services.filter(is_active=True)
        if services:
            return ", ".join([s.name for s in services])
        return "-"
    services_display.short_description = "Services"
    
    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = "Items"


# ==================================================================================
# ITEM TYPE (UPDATED)
# ==================================================================================

# Inline admin for pivot tables
class ItemServiceInline(admin.TabularInline):
    model = ItemService
    extra = 1
    verbose_name = "Service"
    verbose_name_plural = "Services"


class ItemCategoryInline(admin.TabularInline):
    model = ItemCategory
    extra = 1
    verbose_name = "Category"
    verbose_name_plural = "Categories"


class ItemSubcategoryInline(admin.TabularInline):
    model = ItemSubcategory
    extra = 1
    autocomplete_fields = ("subcategory",)
    verbose_name = "Subcategory"
    verbose_name_plural = "Subcategories"


@admin.register(ItemType)
class ItemTypeAdmin(admin.ModelAdmin):
    list_display = (
        "id", "name", "is_active", 
        "services_display", "categories_display", 
        "subcategories_display", "created_at"
    )
    search_fields = ("name", "description")
    list_filter = ("is_active",)
    readonly_fields = ("created_at", "updated_at", "image_preview")
    inlines = [ItemServiceInline, ItemCategoryInline, ItemSubcategoryInline]
    
    fieldsets = (
        ("Basic Information", {
            "fields": ("name", "description", "is_active")
        }),
        ("Media", {
            "fields": ("image_url", "image_preview")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    
    def services_display(self, obj):
        services = obj.services.filter(is_active=True)
        if services:
            return ", ".join([s.name for s in services])
        return "-"
    services_display.short_description = "Services"
    
    def categories_display(self, obj):
        categories = obj.categories.filter(is_active=True)
        if categories:
            return ", ".join([c.name for c in categories])
        return "-"
    categories_display.short_description = "Categories"
    
    def subcategories_display(self, obj):
        subcats = obj.subcategories.filter(is_active=True)
        if subcats:
            return ", ".join([f"{s.category.name}>{s.name}" for s in subcats[:3]])
        return "-"
    subcategories_display.short_description = "Subcategories"
    
    def image_preview(self, obj):
        if obj.image_url:
            return format_html('<img src="{}" width="150" />', obj.image_url)
        return "-"
    image_preview.short_description = "Image Preview"


# ==================================================================================
# ATTRIBUTE TYPE (UPDATED)
# ==================================================================================
@admin.register(AttributeType)
class AttributeTypeAdmin(admin.ModelAdmin):
    list_display = (
        "id", "display_label", "name", "input_type", 
        "is_required", "is_active", "option_count", "created_at"
    )
    search_fields = ("name", "display_label")
    list_filter = ("is_active", "input_type", "is_required")
    filter_horizontal = ("applicable_services", "applicable_items")
    readonly_fields = ("created_at", "updated_at")
    
    fieldsets = (
        ("Basic Information", {
            "fields": ("name", "display_label", "input_type", "is_required", "is_active")
        }),
        ("Applicability", {
            "fields": ("applicable_services", "applicable_items"),
            "description": "Select which services/items use this attribute (optional)"
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    
    def option_count(self, obj):
        return obj.options.filter(is_active=True).count()
    option_count.short_description = "Options"


# ==================================================================================
# ATTRIBUTE OPTION (UPDATED)
# ==================================================================================
@admin.register(AttributeOption)
class AttributeOptionAdmin(admin.ModelAdmin):
    list_display = (
        "id", "name", "attribute_type", "surcharge_display", 
        "is_active", "created_at"
    )
    search_fields = ("name", "attribute_type__name")
    list_filter = ("attribute_type", "is_active")
    autocomplete_fields = ("attribute_type",)
    readonly_fields = ("created_at", "updated_at")
    
    fieldsets = (
        ("Basic Information", {
            "fields": ("attribute_type", "name", "is_active")
        }),
        ("Pricing", {
            "fields": ("surcharge_pct",),
            "description": "Optional % surcharge (e.g., Silk = +10%)"
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    
    def surcharge_display(self, obj):
        if obj.surcharge_pct > 0:
            return format_html('<span style="color: #e74c3c; font-weight: bold;">+{}%</span>', obj.surcharge_pct)
        return "-"
    surcharge_display.short_description = "Surcharge"


# ==================================================================================
# ✨ NEW: DELIVERY TIER
# ==================================================================================
@admin.register(DeliveryTier)
class DeliveryTierAdmin(admin.ModelAdmin):
    list_display = (
        "id", "name", "hours_sla", "surcharge_type", 
        "default_surcharge", "is_active", "created_at"
    )
    search_fields = ("name",)
    list_filter = ("is_active", "surcharge_type")
    readonly_fields = ("created_at", "updated_at")
    
    fieldsets = (
        ("Basic Information", {
            "fields": ("name", "hours_sla", "is_active")
        }),
        ("Surcharge Configuration", {
            "fields": ("surcharge_type", "default_surcharge"),
            "description": "Default surcharge (vendors can override)"
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )


# ==================================================================================
# ADD-ONS, FOLDING, CUSTOMISATION
# ==================================================================================
@admin.register(AddOn)
class AddOnAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "is_active", "created_at")
    search_fields = ("name", "description")
    list_filter = ("is_active",)
    readonly_fields = ("created_at", "updated_at")
    
    fieldsets = (
        ("Basic Information", {
            "fields": ("name", "description", "is_active")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )


@admin.register(FoldingOption)
class FoldingOptionAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "is_active", "created_at")
    search_fields = ("name", "description")
    list_filter = ("is_active",)
    readonly_fields = ("created_at", "updated_at")
    
    fieldsets = (
        ("Basic Information", {
            "fields": ("name", "description", "is_active")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )


@admin.register(CustomisationOption)
class CustomisationOptionAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "is_active", "created_at")
    search_fields = ("name", "description")
    list_filter = ("is_active",)
    readonly_fields = ("created_at", "updated_at")
    
    fieldsets = (
        ("Basic Information", {
            "fields": ("name", "description", "is_active")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )


# ==================================================================================
# PIVOT TABLE ADMINS (Optional - for advanced management)
# ==================================================================================
@admin.register(ItemService)
class ItemServiceAdmin(admin.ModelAdmin):
    list_display = ("item", "service")
    list_filter = ("service",)
    search_fields = ("item__name", "service__name")
    autocomplete_fields = ("item", "service")


@admin.register(ItemCategory)
class ItemCategoryAdmin(admin.ModelAdmin):
    list_display = ("item", "category")
    list_filter = ("category",)
    search_fields = ("item__name", "category__name")
    autocomplete_fields = ("item", "category")


@admin.register(ItemSubcategory)
class ItemSubcategoryAdmin(admin.ModelAdmin):
    list_display = ("item", "subcategory", "category_display")
    list_filter = ("subcategory__category",)
    search_fields = ("item__name", "subcategory__name")
    autocomplete_fields = ("item", "subcategory")
    
    def category_display(self, obj):
        return obj.subcategory.category.name
    category_display.short_description = "Category"


# ==================================================================================
# ❌ REMOVED: VendorAttributeRequest
# ==================================================================================
# Admin creates all AttributeOptions directly
# No vendor requests needed
# ==================================================================================


# ==================================================================================
# ADMIN SITE CUSTOMIZATION
# ==================================================================================
admin.site.site_header = "LaundryOS Admin Panel"
admin.site.site_title = "LaundryOS Admin"
admin.site.index_title = "Catalog Management"