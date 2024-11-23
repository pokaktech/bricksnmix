from django.db.models import Sum

from products.models import Product
from orders.models import OrderItem

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.authentication import TokenAuthentication

from datetime import timedelta, datetime




class GetSellerOrders(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        user = request.user

        # Check if the user is a seller
        if user.profile.user_type != 'seller':
            return Response({'Status': '0', 'message': 'You are not authorized to view products as you are not a seller.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            # If a specific product ID is provided, fetch the product and check if it belongs to the seller
            order_items = OrderItem.objects.filter(product__vendor=user)
            data = []
            for item in order_items:
                data.append({
                    "name": item.product.name,
                    "price": item.product.price,
                    "quantity": item.quantity,
                    "order_from": item.order.delivery_address.city
                })
            # return Response({'Status: 1', 'message': 'Success', })
            return Response({'Status': '1', 'message': 'Success', 'Data': data}, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response({'Status': '0', 'message': 'Product not found or you do not own this product.'}, status=status.HTTP_404_NOT_FOUND)




class SellerTotalCustomerView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    def get(self, request):
        user = request.user
        if user.profile.user_type == "seller":
            order_items = OrderItem.objects.filter(product__vendor=user)
            unique_customers = order_items.values('order__user').distinct().count()

            # Get all products belonging to the seller
            seller_products = Product.objects.filter(vendor=user)

            # Get all orders containing products sold by this seller (current month)
            current_month_start = datetime.now().replace(day=1)
            current_month_customers = (
                OrderItem.objects
                .filter(product__in=seller_products, order__created_at__gte=current_month_start)
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
                    product__in=seller_products,
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
                'Sttaus': '1',
                'message': "You are not a seller"
            })




class SellerTotalRevenueView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    
    def get(self, request):
        user = request.user
        if user.profile.user_type == "seller":
            # Get all products belonging to the seller
            seller_products = Product.objects.filter(vendor=user)
            
            # Calculate total revenue for all time
            total_revenue = OrderItem.objects.filter(
                product__in=seller_products
            ).aggregate(
                total=Sum('price')
            )['total'] or 0
            
            # Current month revenue
            current_month_start = datetime.now().replace(day=1)
            current_month_revenue = OrderItem.objects.filter(
                product__in=seller_products,
                order__created_at__gte=current_month_start
            ).aggregate(
                total=Sum('price')
            )['total'] or 0
            
            # Previous month revenue
            previous_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
            previous_month_end = current_month_start - timedelta(days=1)
            previous_month_revenue = OrderItem.objects.filter(
                product__in=seller_products,
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

class SellerTotalOrderView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    
    def get(self, request):
        user = request.user
        if user.profile.user_type == "seller":
            # Get all orders containing seller's products
            seller_products = Product.objects.filter(vendor=user)
            total_orders = OrderItem.objects.filter(
                product__in=seller_products
            ).values('order').distinct().count()
            
            # Current month orders
            current_month_start = datetime.now().replace(day=1)
            current_month_orders = OrderItem.objects.filter(
                product__in=seller_products,
                order__created_at__gte=current_month_start
            ).values('order').distinct().count()
            
            # Previous month orders
            previous_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
            previous_month_end = current_month_start - timedelta(days=1)
            previous_month_orders = OrderItem.objects.filter(
                product__in=seller_products,
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
                'message': "You are not a seller"
            })
        

class SellerTotalCustomerView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    def get(self, request):
        user = request.user
        if user.profile.user_type == "seller":
            # Fetch all orders and unique customers directly from OrderItem based on the vendor
            order_items = OrderItem.objects.filter(product__vendor=user)
            print(order_items)
            # Fetch all orders containing products sold by this seller
            unique_customers = order_items.values('order__user').distinct()

            # Count the total number of unique customers
            total_customers = unique_customers.count()

            return Response({
                'Status': "1",
                'message': "Success",
                "data": [
                    {
                        "total_customers": total_customers
                    }
                ]
            })
        else:
            return Response({
                'Sttaus': '1',
                'message': "You are not a seller"
            })