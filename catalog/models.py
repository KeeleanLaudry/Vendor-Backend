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