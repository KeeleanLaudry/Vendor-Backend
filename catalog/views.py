from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import IsAdminJWT

from .models import (
    ServiceCategory,
    ItemType,
    AttributeType,
    AttributeOption
)

from .serializers import (
    ServiceCategorySerializer,
    ItemTypeSerializer,
    AttributeTypeSerializer,
    AttributeOptionSerializer
)


class ServiceCategoryViewSet(viewsets.ModelViewSet):

    queryset = ServiceCategory.objects.all()
    serializer_class = ServiceCategorySerializer
    permission_classes = [IsAuthenticated, IsAdminJWT]


class ItemTypeViewSet(viewsets.ModelViewSet):

    queryset = ItemType.objects.all()
    serializer_class = ItemTypeSerializer
    permission_classes = [IsAuthenticated, IsAdminJWT]


class AttributeTypeViewSet(viewsets.ModelViewSet):

    queryset = AttributeType.objects.all()
    serializer_class = AttributeTypeSerializer
    permission_classes = [IsAuthenticated, IsAdminJWT]


class AttributeOptionViewSet(viewsets.ModelViewSet):

    queryset = AttributeOption.objects.all()
    serializer_class = AttributeOptionSerializer
    permission_classes = [IsAuthenticated, IsAdminJWT]