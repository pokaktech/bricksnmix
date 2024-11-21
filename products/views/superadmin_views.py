from django.db.models.aggregates import Count
from django.utils.timezone import now
from datetime import timedelta
from django.db.models import Sum
from django.utils import timezone

from datetime import datetime, timedelta

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.authentication import TokenAuthentication

from products.models import Product
from products.serializers import ProductSerializer


class AdminTotalProductView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    
    def get(self, request):
        user = request.user
        if user.is_superuser:
            # Get total products
            total_products = Product.objects.all().count()
            
            # Current month products
            current_month_start = datetime.now().replace(day=1)
            current_month_products = Product.objects.filter(
                created_at__gte=current_month_start
            ).count()
            
            # Previous month products
            previous_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
            previous_month_end = current_month_start - timedelta(days=1)
            previous_month_products = Product.objects.filter(
                created_at__gte=previous_month_start,
                created_at__lte=previous_month_end
            ).count()
            
            # Calculate percentage change
            if previous_month_products > 0:
                change_percentage = ((current_month_products - previous_month_products) / previous_month_products) * 100
            else:
                change_percentage = 100 if current_month_products > 0 else 0
                
            data = [{
                'total_products': total_products,
                'change_percentage': round(change_percentage, 2)
            }]
            
            return Response({
                'Status': '1',
                'message': 'Success',
                'data': data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'Status': '1',
                'message': "You are not a Super Admin"
            })
        


class AdminTopSellingProductsAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request, *args, **kwargs):
        user = request.user
        if user.is_superuser:
            # Define a time range, e.g., past 30 days
            days_range = 30
            time_threshold = timezone.now() - timedelta(days=days_range)

            # Annotate products with the sum of quantities sold in the given time range
            fast_moving_products = Product.objects.filter(
                orderitem__order__created_at__gte=time_threshold, stock__gt=0
            ).annotate(
                total_sales=Sum('orderitem__quantity')
            ).order_by('-total_sales')[:5]  # Top 5 top selling products

            # Serialize the products (assuming you have a ProductSerializer)
            serializer = ProductSerializer(fast_moving_products, many=True, context={'request': request})
            return Response({"Status": "1", "message": "Success", "Data": serializer.data})