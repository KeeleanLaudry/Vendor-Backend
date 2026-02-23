from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser


# ---------------------------------------
# 1. Vendor (Custom User Model)
# ---------------------------------------
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

    def __str__(self):
        return self.company_name or self.phone
    


# ---------------------------------------
# 2. OTP Model
# ---------------------------------------
class VendorOTP(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expiry = models.DateTimeField()

    def is_valid(self):
        return timezone.now() < self.expiry



# ---------------------------------------
# 3. Vendor Profile
# ---------------------------------------
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

    def __str__(self):
        return self.vendor.company_name or self.vendor.phone


# ---------------------------------------
# 4. Delivery Person
# ---------------------------------------
class DeliveryPerson(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)

    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    vehicle_type = models.CharField(
        max_length=20,
        choices=[("bike", "Bike"), ("car", "Car"), ("van", "Van")]
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.vehicle_type})"



# ---------------------------------------
# 5. Vendor Add-ons
# ---------------------------------------
class VendorAddon(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    key = models.CharField(max_length=100)
    value = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.vendor.company_name or self.vendor.phone} - {self.key}"
