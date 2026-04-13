from django.db import models
from django.utils.text import slugify


# ==================================================================================
# HIERARCHICAL STRUCTURE: Service → Category → Subcategory → ItemType
# Admin creates everything. Vendors only select from dropdowns and set prices.
# ==================================================================================


# ==============================
# Service Categories
# ==============================
# Dry Cleaning, Wash & Fold, Ironing
# ✅ UNCHANGED - Kept as is
class ServiceCategory(models.Model):

    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    description = models.TextField(blank=True, null=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "service_categories"
        verbose_name = "Service Category"  # ✨ ADDED
        verbose_name_plural = "Service Categories"  # ✨ ADDED
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# ==============================
# ✨ NEW: Categories (Gender/Age Groups)
# ==============================
# Male, Female, Kids, Household
# Connected to Services (which services support which categories)
class Category(models.Model):

    name = models.CharField(max_length=120, unique=True)
    
    # Which services support this category
    services = models.ManyToManyField(
        ServiceCategory,
        related_name="categories",
        help_text="Which services are available for this category"
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "categories"
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


# ==============================
# ✨ NEW: Subcategories
# ==============================
# Casual, Formal, Traditional, etc.
# Linked to Category AND Services
class Subcategory(models.Model):

    name = models.CharField(max_length=120)
    
    # Belongs to a category (Male, Female, Kids)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="subcategories"
    )
    
    # Which services support this subcategory
    services = models.ManyToManyField(
        ServiceCategory,
        related_name="subcategories",
        help_text="Which services are available for this subcategory"
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "subcategories"
        verbose_name = "Subcategory"
        verbose_name_plural = "Subcategories"
        ordering = ["category__name", "name"]
        unique_together = [['category', 'name']]

    def __str__(self):
        return f"{self.category.name} > {self.name}"


# ==============================
# Item Types
# ==============================
# Abaya, Blanket, Shirt, Trouser, etc.
# 🔄 MODIFIED - Now linked to Service + Category + Subcategory
class ItemType(models.Model):

    name = models.CharField(max_length=120)
    description = models.TextField(blank=True, null=True)  # ✨ ADDED
    image_url = models.URLField(blank=True, null=True)  # ✨ ADDED

    # 🔄 CHANGED: Now uses pivot tables
    services = models.ManyToManyField(
        ServiceCategory,
        through='ItemService',  # ✨ ADDED explicit through table
        related_name="items"
    )
    
    # ✨ NEW: Link to categories
    categories = models.ManyToManyField(
        Category,
        through='ItemCategory',
        related_name="items"
    )
    
    # ✨ NEW: Link to subcategories
    subcategories = models.ManyToManyField(
        Subcategory,
        through='ItemSubcategory',
        related_name="items"
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # ✨ ADDED

    class Meta:
        db_table = "item_types"
        verbose_name = "Item Type"  # ✨ ADDED
        verbose_name_plural = "Item Types"  # ✨ ADDED
        ordering = ["name"]

    def __str__(self):
        return self.name


# ==============================
# ✨ NEW: Pivot Tables for ItemType
# ==============================

class ItemService(models.Model):
    """Which services support which items"""
    item = models.ForeignKey(ItemType, on_delete=models.CASCADE)
    service = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE)

    class Meta:
        db_table = "item_services"
        unique_together = ['item', 'service']
        verbose_name = "Item-Service Link"
        verbose_name_plural = "Item-Service Links"

    def __str__(self):
        return f"{self.item.name} - {self.service.name}"


class ItemCategory(models.Model):
    """Which categories have which items"""
    item = models.ForeignKey(ItemType, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        db_table = "item_categories"
        unique_together = ['item', 'category']
        verbose_name = "Item-Category Link"
        verbose_name_plural = "Item-Category Links"

    def __str__(self):
        return f"{self.item.name} - {self.category.name}"


class ItemSubcategory(models.Model):
    """Which subcategories have which items"""
    item = models.ForeignKey(ItemType, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE)

    class Meta:
        db_table = "item_subcategories"
        unique_together = ['item', 'subcategory']
        verbose_name = "Item-Subcategory Link"
        verbose_name_plural = "Item-Subcategory Links"

    def __str__(self):
        return f"{self.item.name} - {self.subcategory}"


# ==============================
# Attribute Types
# ==============================
# Fabric, Gender, Weight Range
# 🔄 MODIFIED - Added input_type and display_label
class AttributeType(models.Model):

    INPUT_TYPES = [  # ✨ ADDED
        ('text', 'Text'),
        ('select', 'Select'),
        ('boolean', 'Boolean'),
        ('number', 'Number'),
    ]

    name = models.CharField(max_length=120, unique=True)  # ✨ ADDED unique=True
    display_label = models.CharField(max_length=120, help_text="Label shown in UI")  # ✨ ADDED
    input_type = models.CharField(max_length=20, choices=INPUT_TYPES, default='select')  # ✨ ADDED

    applicable_services = models.ManyToManyField(
        ServiceCategory,
        blank=True,
        related_name="attribute_types"
    )

    applicable_items = models.ManyToManyField(
        ItemType,
        blank=True,
        related_name="attribute_types"
    )

    is_required = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # ✨ ADDED

    class Meta:
        db_table = "attribute_types"
        verbose_name = "Attribute Type"  # ✨ ADDED
        verbose_name_plural = "Attribute Types"  # ✨ ADDED
        ordering = ["name"]

    def __str__(self):
        return self.display_label  # 🔄 CHANGED from self.name


# ==============================
# Attribute Options
# ==============================
# Fabric: Cotton, Silk, Wool
# 🔄 MODIFIED - Added surcharge_pct
class AttributeOption(models.Model):

    attribute_type = models.ForeignKey(
        AttributeType,
        on_delete=models.CASCADE,
        related_name="options"
    )

    name = models.CharField(max_length=120)
    
    # ✨ ADDED: Optional surcharge percentage
    surcharge_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Optional % surcharge (e.g., Silk = +10%)"
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # ✨ ADDED

    class Meta:
        db_table = "attribute_options"
        verbose_name = "Attribute Option"  # ✨ ADDED
        verbose_name_plural = "Attribute Options"  # ✨ ADDED
        ordering = ["attribute_type__name", "name"]  # 🔄 CHANGED ordering
        unique_together = [['attribute_type', 'name']]  # ✨ ADDED

    def __str__(self):
        return f"{self.attribute_type.name}: {self.name}"  # 🔄 CHANGED format


# ==============================
# ✨ NEW: Delivery Tiers
# ==============================
# Standard, Express 2hr, Express 4hr, Next Day
class DeliveryTier(models.Model):

    SURCHARGE_TYPES = [
        ('pct', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]

    name = models.CharField(max_length=100, unique=True)
    hours_sla = models.IntegerField(help_text="Turnaround hours (48, 24, 4, 2)")
    
    surcharge_type = models.CharField(max_length=20, choices=SURCHARGE_TYPES, default='pct')
    default_surcharge = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0,
        help_text="Default surcharge value"
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "delivery_tiers"
        verbose_name = "Delivery Tier"
        verbose_name_plural = "Delivery Tiers"
        ordering = ['hours_sla']

    def __str__(self):
        return f"{self.name} ({self.hours_sla}hrs)"


# ─── ADMIN MANAGED CATALOGUE ───────────────────────────────────────────────

# ==============================
# Add-Ons
# ==============================
# Express, Gift Wrap, Stain Protection
# 🔄 MODIFIED - Added updated_at and Meta
class AddOn(models.Model):
    """General add-on services e.g. Express, Gift Wrap, Stain Protection"""
    name = models.CharField(max_length=100, unique=True)  # ✨ ADDED unique=True
    description = models.TextField(blank=True)
  
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # ✨ ADDED

    class Meta:  # ✨ ADDED
        db_table = "addons"
        verbose_name = "Add-On"
        verbose_name_plural = "Add-Ons"
        ordering = ["name"]

    def __str__(self):
        return self.name


# ==============================
# Folding Options
# ==============================
# Single Fold, Double Fold, Hanging, Rolled
# 🔄 MODIFIED - Added updated_at and Meta
class FoldingOption(models.Model):
    """Folding types e.g. Single Fold, Double Fold, Hanging, Rolled"""
    name = models.CharField(max_length=100, unique=True)  # ✨ ADDED unique=True
    description = models.TextField(blank=True)
   
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # ✨ ADDED

    class Meta:  # ✨ ADDED
        db_table = "folding_options"
        verbose_name = "Folding Option"
        verbose_name_plural = "Folding Options"
        ordering = ["name"]

    def __str__(self):
        return self.name


# ==============================
# Customisation Options
# ==============================
# Monogram, Embroidery, Name Tag
# 🔄 MODIFIED - Added updated_at and Meta
class CustomisationOption(models.Model):
    """Customisation types e.g. Monogram, Embroidery, Name Tag"""
    name = models.CharField(max_length=100, unique=True)  # ✨ ADDED unique=True
    description = models.TextField(blank=True)
   
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # ✨ ADDED

    class Meta:  # ✨ ADDED
        db_table = "customisation_options"
        verbose_name = "Customisation Option"
        verbose_name_plural = "Customisation Options"
        ordering = ["name"]

    def __str__(self):
        return self.name


# ==================================================================================
# ❌ REMOVED MODELS
# ==================================================================================
# These models have been removed and will be replaced in vendors/models.py
#
# ❌ VendorAttributeRequest
#    Why: Admin creates all AttributeOptions directly. No vendor requests needed.
#
# ❌ ItemAddOn
#    Why: Vendors link add-ons when setting prices (in VendorPrice table)
#
# ❌ ItemFolding
#    Why: Vendors link folding options when setting prices
#
# ❌ ItemCustomisation
#    Why: Vendors link customisation when setting prices
#
# All vendor-specific linking now happens in vendors/models.py through:
#   - VendorPrice (core pricing table)
#   - VendorPriceAddOn
#   - VendorPriceFolding
#   - VendorPriceCustomisation
# ==================================================================================
