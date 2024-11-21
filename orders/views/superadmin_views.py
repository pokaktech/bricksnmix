from datetime import timedelta
from django.db.models import Sum


from rest_framework.authentication import TokenAuthentication

from datetime import datetime, timedelta

from orders.models import OrderItem
from products.models import Product

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status




class AdminTotalRevenueView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    
    def get(self, request):
        user = request.user
        if user.is_superuser:
            
            # Calculate total revenue for all time
            total_revenue = OrderItem.objects.all().aggregate(total=Sum('price'))['total'] or 0
            
            # Current month revenue
            current_month_start = datetime.now().replace(day=1)
            current_month_revenue = OrderItem.objects.filter(order__created_at__gte=current_month_start).aggregate(total=Sum('price'))['total'] or 0
            
            # Previous month revenue
            previous_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
            previous_month_end = current_month_start - timedelta(days=1)
            previous_month_revenue = OrderItem.objects.filter(
                order__created_at__gte=previous_month_start,
                order__created_at__lte=previous_month_end
            ).aggregate(
                total=Sum('price')
            )['total'] or 0
            
            # Calculate percentage change
            if previous_month_revenue > 0:
                change_percentage = ((current_month_revenue - previous_month_revenue) / previous_month_revenue) * 100
            else:
                change_percentage = 100 if current_month_revenue > 0 else 0
                
            data = [{
                'total_revenue': total_revenue,
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
                'message': "You are not a seller"
            })
        


class AdminTotalOrderView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    
    def get(self, request):
        user = request.user
        if user.is_superuser:
            # Get all orders containing seller's products
            # seller_products = Product.objects.filter(vendor=user)
            total_orders = OrderItem.objects.all().values('order').distinct().count()
            
            # Current month orders
            current_month_start = datetime.now().replace(day=1)
            current_month_orders = OrderItem.objects.filter(order__created_at__gte=current_month_start).values('order').distinct().count()
            
            # Previous month orders
            previous_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
            previous_month_end = current_month_start - timedelta(days=1)
            previous_month_orders = OrderItem.objects.filter(
                order__created_at__gte=previous_month_start,
                order__created_at__lte=previous_month_end
            ).values('order').distinct().count()
            
            # Calculate percentage change
            if previous_month_orders > 0:
                change_percentage = ((current_month_orders - previous_month_orders) / previous_month_orders) * 100
            else:
                change_percentage = 100 if current_month_orders > 0 else 0
                
            data = [{
                'total_orders': total_orders,
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
        



class AdminTotalCustomerView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    def get(self, request):
        user = request.user
        if user.is_superuser:
            order_items = OrderItem.objects.all()
            unique_customers = order_items.values('order__user').distinct().count()

            # Get all products belonging to the seller
            seller_products = Product.objects.all()

            # Get all orders containing products sold by this seller (current month)
            current_month_start = datetime.now().replace(day=1)
            current_month_customers = (
                OrderItem.objects
                .filter(order__created_at__gte=current_month_start)
                .values('order__user')
                .distinct()
            )
            total_customers_current = current_month_customers.count()

            # Get the previous month date range
            previous_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
            previous_month_end = current_month_start - timedelta(days=1)

            # Get total customers for the previous month
            previous_month_customers = (
                OrderItem.objects
                .filter(
                    order__created_at__gte=previous_month_start,
                    order__created_at__lte=previous_month_end
                )
                .values('order__user')
                .distinct()
            )
            total_customers_previous = previous_month_customers.count()

            # Calculate the percentage change
            if total_customers_previous > 0:
                change_percentage = ((total_customers_current - total_customers_previous) / total_customers_previous) * 100
            else:
                change_percentage = 100 if total_customers_current > 0 else 0
            data = [{
                'total_customers': unique_customers,
                # 'total_customers_previous': total_customers_previous,
                'change_percentage': round(change_percentage, 2)
            }]
            # Prepare the response data
            response_data = {
                'Status': '1',
                'message': 'Success',
                "data": data
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response({
                'Status': '1',
                'message': "You are not a Super Admin"
            })
        


