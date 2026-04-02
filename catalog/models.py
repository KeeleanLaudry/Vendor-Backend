from django.db import models
from django.utils.text import slugify


# ==============================
# Service Categories
# ==============================
#Dry Cleaning
#Wash & Fold
#Ironing
class ServiceCategory(models.Model):

    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    description = models.TextField(blank=True, null=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "service_categories"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# ==============================
# Item Types
# ==============================
#Abaya
#Blanket
class ItemType(models.Model):

    name = models.CharField(max_length=120)

    services = models.ManyToManyField(
        ServiceCategory,
        related_name="items"
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "item_types"
        ordering = ["name"]

    def __str__(self):
        return self.name


# ==============================
# Attribute Types
# ==============================
#Fabric
#Gender
#Weight Range
class AttributeType(models.Model):

    name = models.CharField(max_length=120)

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

    class Meta:
        db_table = "attribute_types"
        ordering = ["name"]

    def __str__(self):
        return self.name


# ==============================
# Attribute Options
# ==============================
#Fabric:
#Cotton
#Silk
#Wool
class AttributeOption(models.Model):

    attribute_type = models.ForeignKey(
        AttributeType,
        on_delete=models.CASCADE,
        related_name="options"
    )

    name = models.CharField(max_length=120)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "attribute_options"
        ordering = ["name"]

    def __str__(self):
        return f"{self.attribute_type.name} - {self.name}"


# ==============================
# Vendor Attribute Request
# ==============================

class VendorAttributeRequest(models.Model):

    attribute_type = models.ForeignKey(
        AttributeType,
        on_delete=models.CASCADE
    )

    requested_value = models.CharField(max_length=120)

    vendor_id = models.IntegerField()  # later replace with FK to vendor model

    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        default="pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "vendor_attribute_requests"

    def __str__(self):
        return f"{self.requested_value} ({self.status})"
    from django.db import models


# ─── ADMIN MANAGED CATALOGUE ───────────────────────────────────────────────

class AddOn(models.Model):
    """General add-on services e.g. Express, Gift Wrap, Stain Protection"""
    name        = models.CharField(max_length=100)
    description = models.TextField(blank=True)
  
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class FoldingOption(models.Model):
    """Folding types e.g. Single Fold, Double Fold, Hanging, Rolled"""
    name        = models.CharField(max_length=100)
    description = models.TextField(blank=True)
   
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class CustomisationOption(models.Model):
    """Customisation types e.g. Monogram, Embroidery, Name Tag"""
    name        = models.CharField(max_length=100)
    description = models.TextField(blank=True)
   
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# ─── VENDOR LINKS TO ITEM ──────────────────────────────────────────────────

class ItemAddOn(models.Model):
    """Vendor attaches an AddOn to one of their ItemTypes"""
    item_type   = models.ForeignKey('ItemType', on_delete=models.CASCADE, related_name='addons')
    addon       = models.ForeignKey(AddOn, on_delete=models.CASCADE, related_name='item_addons')

    class Meta:
        unique_together = ('item_type', 'addon')

    def __str__(self):
        return f"{self.item_type} → {self.addon}"


class ItemFolding(models.Model):
    """Vendor attaches a FoldingOption to one of their ItemTypes"""
    item_type      = models.ForeignKey('ItemType', on_delete=models.CASCADE, related_name='folding_options')
    folding_option = models.ForeignKey(FoldingOption, on_delete=models.CASCADE, related_name='item_foldings')

    class Meta:
        unique_together = ('item_type', 'folding_option')

    def __str__(self):
        return f"{self.item_type} → {self.folding_option}"


class ItemCustomisation(models.Model):
    """Vendor attaches a CustomisationOption to one of their ItemTypes"""
    item_type            = models.ForeignKey('ItemType', on_delete=models.CASCADE, related_name='customisation_options')
    customisation_option = models.ForeignKey(CustomisationOption, on_delete=models.CASCADE, related_name='item_customisations')

    class Meta:
        unique_together = ('item_type', 'customisation_option')

    def __str__(self):
        return f"{self.item_type} → {self.customisation_option}"