from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import pre_save
from django.dispatch import receiver

from catalog.models import (
    ServiceCategory,
    Category,  # ✨ NEW
    Subcategory,  # ✨ NEW
    ItemType,
    AttributeOption,
    DeliveryTier,  # ✨ NEW
    AddOn,
    FoldingOption,
    CustomisationOption,
)


# ---------------------------------------
# 1. Vendor (Custom User Model)
# ---------------------------------------
# ✅ UNCHANGED - Kept as is
class Vendor(AbstractUser):

    # Remove default username
    username = None

    # Remove unused default fields
    first_name = None
    last_name = None
    email = None  # IMPORTANT → remove default email field

    # Your login field
    phone = models.CharField(max_length=20, unique=True)

    # Optional fields
    company_name = models.CharField(max_length=200, blank=True, null=True)

    is_verified = models.BooleanField(default=False)

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('activated', 'Activated'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    rejection_reason = models.TextField(blank=True, null=True)
    extra_info = models.JSONField(blank=True, null=True)

    role = models.CharField(max_length=20, default="vendor")

    created_at = models.DateTimeField(auto_now_add=True)

    # 🔥 CRITICAL FOR CUSTOM AUTH
    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []

    class Meta:
    
        verbose_name = "Vendor"  # ✨ ADDED
        verbose_name_plural = "Vendors"  # ✨ ADDED

    def __str__(self):
        return self.company_name or self.phone


# ---------------------------------------
# 2. OTP Model
# ---------------------------------------
# ✅ UNCHANGED - Kept as is
class VendorOTP(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expiry = models.DateTimeField()

    class Meta:
        db_table = "vendor_otps"  # ✨ ADDED
        verbose_name = "Vendor OTP"  # ✨ ADDED
        verbose_name_plural = "Vendor OTPs"  # ✨ ADDED

    def is_valid(self):
        return timezone.now() < self.expiry

    def __str__(self):
        return f"{self.vendor.phone} - {self.otp}"


# ---------------------------------------
# 3. Vendor Profile
# ---------------------------------------
# ✅ UNCHANGED - Kept as is
class VendorProfile(models.Model):
    vendor = models.OneToOneField(Vendor, on_delete=models.CASCADE)

    company_name = models.CharField(max_length=200, blank=True, null=True)

    # Business Documents (Step 1)
    trade_license = models.FileField(
        upload_to="vendor/trade_license/",
        blank=True,
        null=True
    )
    ejari = models.FileField(
        upload_to="vendor/ejari/",
        blank=True,
        null=True
    )
    logo = models.ImageField(
        upload_to="vendor/logo/",
        blank=True,
        null=True
    )

    trade_name_document = models.CharField(max_length=200, blank=True, null=True)

    # Contact Fields (Step 3)
    landline = models.CharField(max_length=20, blank=True, null=True)
    whatsapp_number = models.CharField(max_length=20, blank=True, null=True)

    # Bank Details (Step 1)
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    account_holder_name = models.CharField(max_length=100, blank=True, null=True)
    account_number = models.CharField(max_length=50, blank=True, null=True)
    iban_number = models.CharField(max_length=34, blank=True, null=True)
    is_profile_completed = models.BooleanField(default=False)
    
    # Location (Step 2)
    address = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    delivery_radius_km = models.IntegerField(default=0, blank=True, null=True)

    # Optional Documents
    emirates_id = models.FileField(upload_to="vendor/emirates_id/", blank=True, null=True)
    vat_certificate = models.FileField(upload_to="vendor/vat_certificate/", blank=True, null=True)
    corporate_tax_certificate = models.FileField(upload_to="vendor/corporate_tax/", blank=True, null=True)

    # Optional Social
    instagram = models.URLField(blank=True, null=True)
    facebook = models.URLField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    # Future Proof
    extra_fields = models.JSONField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # ✨ ADDED

    class Meta:
        db_table = "vendor_profiles"  # ✨ ADDED
        verbose_name = "Vendor Profile"  # ✨ ADDED
        verbose_name_plural = "Vendor Profiles"  # ✨ ADDED

    def __str__(self):
        return self.vendor.company_name or self.vendor.phone


# ---------------------------------------
# 4. Delivery Person
# ---------------------------------------
# ✅ UNCHANGED - Kept as is
class DeliveryPerson(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)

    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    vehicle_type = models.CharField(
        max_length=20,
        choices=[("bike", "Bike"), ("car", "Car"), ("van", "Van")]
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "delivery_persons"  # ✨ ADDED
        verbose_name = "Delivery Person"  # ✨ ADDED
        verbose_name_plural = "Delivery Persons"  # ✨ ADDED

    def __str__(self):
        return f"{self.name} ({self.vehicle_type})"


# ---------------------------------------
# 5. Vendor Add-ons
# ---------------------------------------
# ✅ UNCHANGED - Kept as is
class VendorAddon(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    key = models.CharField(max_length=100)
    value = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "vendor_addons"  # ✨ ADDED
        verbose_name = "Vendor Addon"  # ✨ ADDED
        verbose_name_plural = "Vendor Addons"  # ✨ ADDED

    def __str__(self):
        return f"{self.vendor.company_name or self.vendor.phone} - {self.key}"


# ==================================================================================
# 🔄 REFACTORED: VENDOR PRICING (Following LaundryOS Spec)
# ==================================================================================
# This replaces VendorServicePricing with hierarchical structure
# ==================================================================================


# ---------------------------------------
# 6. Vendor Price (CORE PRICING TABLE)
# ---------------------------------------
class VendorPrice(models.Model):
    """
    Core pricing table - ONE price per unique combination
    Vendor selects: Service → Category → Subcategory → Item → Delivery Tier
    Then sets the BASE PRICE
    """
    
    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.CASCADE,
        related_name='prices'
    )
    
    # ✨ HIERARCHICAL SELECTION (Admin-created catalog)
    service = models.ForeignKey(
        ServiceCategory,
        on_delete=models.PROTECT,
        help_text="Service: Dry Cleaning, Wash & Fold, Ironing"
    )
    
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        help_text="Category: Male, Female, Kids"
    )
    
    subcategory = models.ForeignKey(
        Subcategory,
        on_delete=models.PROTECT,
        help_text="Subcategory: Casual, Formal, Traditional"
    )
    
    item = models.ForeignKey(
        ItemType,
        on_delete=models.PROTECT,
        help_text="Item: Shirt, Trouser, Saree, Abaya"
    )
    
    # Optional: Delivery tier (NULL = Standard)
    delivery_tier = models.ForeignKey(
        DeliveryTier,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        help_text="NULL = Standard tier | Express 2hr, Express 4hr, etc."
    )
    
    # BASE PRICE for this combination
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Base price in AED for this exact combination"
    )
    
    # Optional fields from your original model
    image = models.ImageField(
        upload_to="vendor_services/",
        null=True,
        blank=True,
        help_text="Optional item image"
    )
    
    turnaround_time = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="E.g., '24 hours', '2-3 days'"
    )
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "vendor_prices"
        verbose_name = "Vendor Price"
        verbose_name_plural = "Vendor Prices"
        # ✨ UNIQUE CONSTRAINT: One price per vendor per complete combination
        unique_together = [
            ['vendor', 'service', 'category', 'subcategory', 'item', 'delivery_tier']
        ]
        indexes = [
            models.Index(fields=['vendor']),
            models.Index(fields=['service', 'category', 'subcategory', 'item']),
        ]
        ordering = ['-updated_at']

    def __str__(self):
        tier_str = f" - {self.delivery_tier.name}" if self.delivery_tier else " - Standard"
        return (
            f"{self.vendor.company_name or self.vendor.phone}: "
            f"{self.service.name} > {self.category.name} > {self.subcategory.name} > {self.item.name}"
            f"{tier_str} = AED {self.price}"
        )


# ---------------------------------------
# 7. Vendor Price - Attribute Options
# ---------------------------------------
class VendorPriceAttribute(models.Model):
    """
    Links specific attribute options to a vendor price
    E.g., "Shirt + Ironing" supports Fabric=[Cotton, Silk, Wool]
    """
    
    vendor_price = models.ForeignKey(
        VendorPrice,
        on_delete=models.CASCADE,
        related_name='attribute_selections'
    )
    
    attribute_option = models.ForeignKey(
        AttributeOption,
        on_delete=models.PROTECT,
        help_text="Admin-created attribute option (e.g., Cotton, Silk)"
    )
    
    # Optional: Vendor can override the default surcharge
    custom_surcharge_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Override AttributeOption.surcharge_pct (leave blank to use default)"
    )

    class Meta:
        db_table = "vendor_price_attributes"
        unique_together = ['vendor_price', 'attribute_option']
        verbose_name = "Vendor Price Attribute"
        verbose_name_plural = "Vendor Price Attributes"

    def __str__(self):
        return f"{self.vendor_price.item.name} → {self.attribute_option}"
    
    def get_effective_surcharge(self):
        """Returns the effective surcharge % (custom or default)"""
        if self.custom_surcharge_pct is not None:
            return self.custom_surcharge_pct
        return self.attribute_option.surcharge_pct


# ---------------------------------------
# 8. Vendor Price - Add-Ons
# ---------------------------------------
class VendorPriceAddOn(models.Model):
    """
    Vendor offers specific add-ons for their items
    E.g., "Shirt + Ironing" can have add-on [Express, Gift Wrap] with vendor-set prices
    """
    
    vendor_price = models.ForeignKey(
        VendorPrice,
        on_delete=models.CASCADE,
        related_name='addon_options'
    )
    
    addon = models.ForeignKey(
        AddOn,
        on_delete=models.PROTECT,
        help_text="Admin-created add-on"
    )
    
    # Vendor sets price for this add-on
    addon_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price for this add-on in AED"
    )

    class Meta:
        db_table = "vendor_price_addons"
        unique_together = ['vendor_price', 'addon']
        verbose_name = "Vendor Price Add-On"
        verbose_name_plural = "Vendor Price Add-Ons"

    def __str__(self):
        return f"{self.vendor_price.item.name} → {self.addon.name} (+AED {self.addon_price})"


# ---------------------------------------
# 9. Vendor Price - Folding Options
# ---------------------------------------
class VendorPriceFolding(models.Model):
    """
    Vendor offers folding options for their items
    E.g., "Shirt" can be [Single Fold, Hanging] with optional prices
    """
    
    vendor_price = models.ForeignKey(
        VendorPrice,
        on_delete=models.CASCADE,
        related_name='folding_options'
    )
    
    folding_option = models.ForeignKey(
        FoldingOption,
        on_delete=models.PROTECT,
        help_text="Admin-created folding option"
    )
    
    # Vendor sets price for this folding (can be 0 if free)
    folding_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Additional price for this folding (0 if free)"
    )

    class Meta:
        db_table = "vendor_price_folding"
        unique_together = ['vendor_price', 'folding_option']
        verbose_name = "Vendor Price Folding"
        verbose_name_plural = "Vendor Price Folding Options"

    def __str__(self):
        price_str = f"+AED {self.folding_price}" if self.folding_price > 0 else "Free"
        return f"{self.vendor_price.item.name} → {self.folding_option.name} ({price_str})"


# ---------------------------------------
# 10. Vendor Price - Customisation Options
# ---------------------------------------
class VendorPriceCustomisation(models.Model):
    """
    Vendor offers customisation for their items
    E.g., "Shirt" can have [Monogram, Embroidery] with vendor-set prices
    """
    
    vendor_price = models.ForeignKey(
        VendorPrice,
        on_delete=models.CASCADE,
        related_name='customisation_options'
    )
    
    customisation_option = models.ForeignKey(
        CustomisationOption,
        on_delete=models.PROTECT,
        help_text="Admin-created customisation option"
    )
    
    # Vendor sets price for this customisation
    customisation_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price for this customisation in AED"
    )

    class Meta:
        db_table = "vendor_price_customisations"
        unique_together = ['vendor_price', 'customisation_option']
        verbose_name = "Vendor Price Customisation"
        verbose_name_plural = "Vendor Price Customisations"

    def __str__(self):
        return f"{self.vendor_price.item.name} → {self.customisation_option.name} (+AED {self.customisation_price})"


# ---------------------------------------
# 11. Vendor Price Audit Log
# ---------------------------------------
class VendorPriceAudit(models.Model):
    """
    Automatic audit trail for every price change
    Written by Django signal
    """
    
    vendor_price = models.ForeignKey(
        VendorPrice,
        on_delete=models.SET_NULL,
        null=True
    )
    
    old_price = models.DecimalField(max_digits=10, decimal_places=2)
    new_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    changed_by = models.ForeignKey(
        Vendor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "vendor_price_audit"
        verbose_name = "Price Audit Log"
        verbose_name_plural = "Price Audit Logs"
        ordering = ['-changed_at']

    def __str__(self):
        return f"{self.vendor_price} changed from AED {self.old_price} to AED {self.new_price}"


# ==================================================================================
# SIGNAL: Auto-write audit log on price change
# ==================================================================================

@receiver(pre_save, sender=VendorPrice)
def log_price_change(sender, instance, **kwargs):
    """Automatically log price changes"""
    if instance.pk:
        try:
            old = VendorPrice.objects.get(pk=instance.pk)
            if old.price != instance.price:
                VendorPriceAudit.objects.create(
                    vendor_price=instance,
                    old_price=old.price,
                    new_price=instance.price,
                    changed_by=instance.vendor
                )
        except VendorPrice.DoesNotExist:
            pass


# ==================================================================================
# ❌ REMOVED MODEL
# ==================================================================================
# VendorServicePricing has been replaced by:
#   - VendorPrice (hierarchical: service → category → subcategory → item)
#   - VendorPriceAttribute (attribute options with surcharges)
#   - VendorPriceAddOn (add-ons with prices)
#   - VendorPriceFolding (folding options with prices)
#   - VendorPriceCustomisation (customisation options with prices)
#   - VendorPriceAudit (automatic audit trail)
# ==================================================================================