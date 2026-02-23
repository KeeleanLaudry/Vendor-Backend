from django.urls import path
from .views import request_otp, verify_otp,upload_profile,get_vendor_profile

urlpatterns = [
    path("request-otp/", request_otp),
    path("verify-otp/", verify_otp),
     path("upload-profile/",upload_profile),
    path("get-profile/",get_vendor_profile),
]
