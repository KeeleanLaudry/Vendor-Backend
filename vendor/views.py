from rest_framework.decorators import api_view, parser_classes, permission_classes, authentication_classes
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny
from django.db import transaction
from django.db.models import Q, Count, Avg
from django.http import HttpResponse
import csv
import io

from .authentication import VendorJWTAuthentication
from .permissions import IsVendorJWT

from .serializers import (
    RequestOTPSerializer,
    VerifyOTPSerializer,
    VendorProfileSerializer,
    VendorPricingSerializer,
    VendorPricingBulkCreateSerializer,
    VendorPricingCSVSerializer,
    VendorPricingStatsSerializer,
    VendorPricingTemplateSerializer
)

from .models import (
    VendorProfile,
    VendorPricing,
    VendorPricingTemplate
)

from catalog.models import (
    ServiceCategory,
    Category,
    Subcategory,
    ItemType,
)


# ==================================================================================
# AUTHENTICATION VIEWS
# ==================================================================================

@api_view(['POST'])
@permission_classes([AllowAny])
def request_otp(request):
    serializer = RequestOTPSerializer(data=request.data)
    if serializer.is_valid():
        data = serializer.save()
        return Response({
            "message": "OTP sent",
            "vendor_id": data["vendor_id"]
        })
    return Response(serializer.errors, status=400)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp(request):
    serializer = VerifyOTPSerializer(data=request.data)
    if serializer.is_valid():
        return Response(serializer.save())
    return Response(serializer.errors, status=400)


@api_view(['POST'])
@authentication_classes([VendorJWTAuthentication])
@permission_classes([IsVendorJWT])
@parser_classes([MultiPartParser, FormParser])
def upload_profile(request):
    vendor = request.user

    profile, created = VendorProfile.objects.get_or_create(vendor=vendor)

    data = request.data.copy()
    for key, value in list(data.items()):
        if value in ["", None]:
            data.pop(key)

    serializer = VendorProfileSerializer(profile, data=data, partial=True)

    if serializer.is_valid():
        serializer.save()
        profile.is_profile_completed = True
        profile.save(update_fields=["is_profile_completed"])

        return Response({
            "message": "Profile saved successfully",
            "created": created,
            "profile_completed": True
        })

    return Response(serializer.errors, status=400)


@api_view(['GET'])
@authentication_classes([VendorJWTAuthentication])
@permission_classes([IsVendorJWT])
def get_vendor_profile(request):
    vendor = request.user

    profile, created = VendorProfile.objects.get_or_create(vendor=vendor)

    serializer = VendorProfileSerializer(profile)
    return Response({
        "profile": serializer.data,
        "is_new": created
    })


# ==================================================================================
# VENDOR PRICING VIEWSET
# ==================================================================================

class VendorPricingViewSet(viewsets.ModelViewSet):
    serializer_class = VendorPricingSerializer
    authentication_classes = [VendorJWTAuthentication]
    permission_classes = [IsVendorJWT]

    def get_queryset(self):
        return VendorPricing.objects.filter(vendor=self.request.user).select_related(
            'service', 'category', 'subcategory', 'item'
        )

    def perform_create(self, serializer):
        serializer.save(vendor=self.request.user)

    # ─── BULK CREATE ───
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        serializer = VendorPricingBulkCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service_ids = serializer.validated_data.get('service_ids', [])
        category_ids = serializer.validated_data.get('category_ids', [])
        subcategory_ids = serializer.validated_data.get('subcategory_ids', [])
        item_ids = serializer.validated_data.get('item_ids', [])
        base_price = serializer.validated_data['base_price']

        vendor = request.user
        created_count = 0
        skipped_count = 0
        pricing_entries = []

        if not any([service_ids, category_ids, subcategory_ids, item_ids]):
            pricing, created = VendorPricing.objects.get_or_create(
                vendor=vendor, service=None, category=None,
                subcategory=None, item=None,
                defaults={'base_price': base_price}
            )
            if created:
                created_count += 1
                pricing_entries.append(pricing)
            else:
                pricing.base_price = base_price
                pricing.save()
                skipped_count += 1
        else:
            if service_ids and not category_ids and not subcategory_ids and not item_ids:
                for service_id in service_ids:
                    pricing, created = VendorPricing.objects.get_or_create(
                        vendor=vendor, service_id=service_id, category=None,
                        subcategory=None, item=None,
                        defaults={'base_price': base_price}
                    )
                    if created:
                        created_count += 1
                        pricing_entries.append(pricing)
                    else:
                        pricing.base_price = base_price
                        pricing.save()
                        skipped_count += 1

            elif service_ids and category_ids and not subcategory_ids and not item_ids:
                for service_id in service_ids:
                    for category_id in category_ids:
                        pricing, created = VendorPricing.objects.get_or_create(
                            vendor=vendor, service_id=service_id, category_id=category_id,
                            subcategory=None, item=None,
                            defaults={'base_price': base_price}
                        )
                        if created:
                            created_count += 1
                            pricing_entries.append(pricing)
                        else:
                            pricing.base_price = base_price
                            pricing.save()
                            skipped_count += 1

            elif service_ids and category_ids and subcategory_ids and item_ids:
                for service_id in service_ids:
                    for category_id in category_ids:
                        for subcategory_id in subcategory_ids:
                            for item_id in item_ids:
                                pricing, created = VendorPricing.objects.get_or_create(
                                    vendor=vendor, service_id=service_id,
                                    category_id=category_id, subcategory_id=subcategory_id,
                                    item_id=item_id,
                                    defaults={'base_price': base_price}
                                )
                                if created:
                                    created_count += 1
                                    pricing_entries.append(pricing)
                                else:
                                    pricing.base_price = base_price
                                    pricing.save()
                                    skipped_count += 1

        return Response({
            'created': created_count,
            'updated': skipped_count,
            'total': created_count + skipped_count,
            'message': f'Created {created_count} new pricing rules, updated {skipped_count} existing rules'
        }, status=status.HTTP_201_CREATED)

    # ─── BULK UPDATE ───
    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        ids = request.data.get('ids', [])
        base_price = request.data.get('base_price')

        if not ids:
            return Response({'error': 'No IDs provided'}, status=status.HTTP_400_BAD_REQUEST)
        if base_price is None:
            return Response({'error': 'base_price is required'}, status=status.HTTP_400_BAD_REQUEST)

        updated = VendorPricing.objects.filter(
            vendor=request.user, id__in=ids
        ).update(base_price=base_price)

        return Response({'updated': updated, 'message': f'Updated {updated} pricing rules'})

    # ─── BULK DELETE ───
    @action(detail=False, methods=['post'])
    def bulk_delete(self, request):
        ids = request.data.get('ids', [])

        if not ids:
            return Response({'error': 'No IDs provided'}, status=status.HTTP_400_BAD_REQUEST)

        deleted, _ = VendorPricing.objects.filter(
            vendor=request.user, id__in=ids
        ).delete()

        return Response({'deleted': deleted, 'message': f'Deleted {deleted} pricing rules'})

    # ─── STATS ───
    @action(detail=False, methods=['get'])
    def stats(self, request):
        vendor = request.user

        total_rules = VendorPricing.objects.filter(vendor=vendor, is_active=True).count()
        total_items = ItemType.objects.filter(is_active=True).count()
        items_with_pricing = VendorPricing.objects.filter(
            vendor=vendor, is_active=True, item__isnull=False
        ).values('item').distinct().count()

        coverage = (items_with_pricing / total_items * 100) if total_items > 0 else 0

        pricing_by_level = VendorPricing.objects.filter(
            vendor=vendor, is_active=True
        ).values('pricing_level').annotate(count=Count('id'))
        pricing_by_level_dict = {item['pricing_level']: item['count'] for item in pricing_by_level}

        avg_price = VendorPricing.objects.filter(
            vendor=vendor, is_active=True
        ).aggregate(avg=Avg('base_price'))['avg'] or 0

        data = {
            'total_rules': total_rules,
            'coverage_percentage': round(coverage, 2),
            'missing_items_count': total_items - items_with_pricing,
            'pricing_by_level': pricing_by_level_dict,
            'average_price': round(avg_price, 2)
        }

        serializer = VendorPricingStatsSerializer(data)
        return Response(serializer.data)

    # ─── SPREADSHEET VIEW (now supports item_id filter) ───
    @action(detail=False, methods=['get'])
    def spreadsheet_view(self, request):
        vendor = request.user

        service_id = request.query_params.get('service_id')
        category_id = request.query_params.get('category_id')
        subcategory_id = request.query_params.get('subcategory_id')
        item_id = request.query_params.get('item_id')  # ✨ NEW

        items = ItemType.objects.filter(is_active=True).prefetch_related(
            'services', 'categories', 'subcategories'
        ).distinct()

        if service_id:
            items = items.filter(services__id=service_id)
        if category_id:
            items = items.filter(categories__id=category_id)
        if subcategory_id:
            items = items.filter(subcategories__id=subcategory_id)
        if item_id:  # ✨ NEW
            items = items.filter(id=item_id)

        rows = []
        for item in items:
            for service in item.services.filter(is_active=True):
                if service_id and str(service.id) != str(service_id):
                    continue
                for category in item.categories.filter(is_active=True):
                    if category_id and str(category.id) != str(category_id):
                        continue
                    for subcategory in item.subcategories.filter(category=category, is_active=True):
                        if subcategory_id and str(subcategory.id) != str(subcategory_id):
                            continue

                        price, price_obj = VendorPricing.get_price_for_item(
                            vendor_id=vendor.id,
                            service_id=service.id,
                            category_id=category.id,
                            subcategory_id=subcategory.id,
                            item_id=item.id
                        )
                        rows.append({
                            'pricing_id': price_obj.id if price_obj else None,
                            'service_id': service.id,
                            'service_name': service.name,
                            'category_id': category.id,
                            'category_name': category.name,
                            'subcategory_id': subcategory.id,
                            'subcategory_name': subcategory.name,
                            'item_id': item.id,
                            'item_name': item.name,
                            'base_price': float(price) if price else None,
                            'pricing_level': price_obj.pricing_level if price_obj else None,
                            'has_price': price is not None
                        })

        return Response({'count': len(rows), 'results': rows})

    # ─── IMPORT CSV ───
    @action(detail=False, methods=['post'])
    def import_csv(self, request):
        csv_file = request.FILES.get('file')

        if not csv_file:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
        if not csv_file.name.endswith('.csv'):
            return Response({'error': 'File must be CSV format'}, status=status.HTTP_400_BAD_REQUEST)

        vendor = request.user
        created_count = 0
        updated_count = 0
        errors = []

        try:
            decoded_file = csv_file.read().decode('utf-8')
            csv_data = csv.DictReader(io.StringIO(decoded_file))

            with transaction.atomic():
                for row_num, row in enumerate(csv_data, start=2):
                    try:
                        service_name = row.get('service', '').strip()
                        category_name = row.get('category', '').strip()
                        subcategory_name = row.get('subcategory', '').strip()
                        item_name = row.get('item', '').strip()
                        price = float(row.get('price', 0))

                        service = ServiceCategory.objects.filter(name=service_name).first() if service_name else None
                        category = Category.objects.filter(name=category_name).first() if category_name else None
                        subcategory = Subcategory.objects.filter(name=subcategory_name).first() if subcategory_name else None
                        item = ItemType.objects.filter(name=item_name).first() if item_name else None

                        pricing, created = VendorPricing.objects.update_or_create(
                            vendor=vendor, service=service, category=category,
                            subcategory=subcategory, item=item,
                            defaults={'base_price': price}
                        )

                        if created:
                            created_count += 1
                        else:
                            updated_count += 1

                    except Exception as e:
                        errors.append(f"Row {row_num}: {str(e)}")

            return Response({
                'created': created_count,
                'updated': updated_count,
                'errors': errors,
                'message': f'Imported {created_count + updated_count} pricing rules'
            })

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ─── EXPORT CSV ───
    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        vendor = request.user
        pricing_rules = VendorPricing.objects.filter(vendor=vendor, is_active=True).select_related(
            'service', 'category', 'subcategory', 'item'
        )

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['service', 'category', 'subcategory', 'item', 'price'])

        for pricing in pricing_rules:
            writer.writerow([
                pricing.service.name if pricing.service else '',
                pricing.category.name if pricing.category else '',
                pricing.subcategory.name if pricing.subcategory else '',
                pricing.item.name if pricing.item else '',
                str(pricing.base_price)
            ])

        response = HttpResponse(output.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="vendor_pricing_{vendor.id}.csv"'
        return response


# ==================================================================================
# VENDOR PRICING TEMPLATE VIEWSET
# ==================================================================================

class VendorPricingTemplateViewSet(viewsets.ModelViewSet):
    serializer_class = VendorPricingTemplateSerializer
    authentication_classes = [VendorJWTAuthentication]
    permission_classes = [IsVendorJWT]

    def get_queryset(self):
        return VendorPricingTemplate.objects.filter(vendor=self.request.user)

    def perform_create(self, serializer):
        serializer.save(vendor=self.request.user)

    @action(detail=True, methods=['post'])
    def apply(self, request, pk=None):
        template = self.get_object()
        vendor = request.user
        created_count = 0

        with transaction.atomic():
            for template_item in template.items.all():
                pricing, created = VendorPricing.objects.get_or_create(
                    vendor=vendor,
                    service=template_item.service,
                    category=template_item.category,
                    subcategory=template_item.subcategory,
                    item=template_item.item,
                    defaults={'base_price': template_item.base_price}
                )
                if created:
                    created_count += 1
                else:
                    pricing.base_price = template_item.base_price
                    pricing.save()

        return Response({
            'message': f'Applied template "{template.name}", created {created_count} pricing rules'
        })