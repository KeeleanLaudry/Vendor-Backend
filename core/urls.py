from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def home(request):
    return JsonResponse({
        "status": "success",
        "message": "Laundry API is running 🚀"
    })

urlpatterns = [
    path('', home),   # 👈 add this
    path('admin/', admin.site.urls),
    path("vendor/", include("vendor.urls")),
    path("accounts/", include("accounts.urls")),
    path("api/admin/catalog/", include("catalog.urls")),
]
