from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .serializers import AdminLoginSerializer
from .permissions import IsAdminJWT

@api_view(["POST"])
@permission_classes([AllowAny])
def admin_login(request):
    serializer = AdminLoginSerializer(data=request.data)
    if serializer.is_valid():
        return Response(serializer.save())
    return Response(serializer.errors, status=400)

@api_view(["GET"])
@permission_classes([IsAdminJWT])
def admin_dashboard(request):
    return Response({"message": "Welcome Admin"})