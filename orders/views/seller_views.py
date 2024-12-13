from django.db.models import Sum, Count


from products.models import Product
from orders.models import *
from accounts.consumers import store_notification, send_message_to_customer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import ValidationError

from datetime import timedelta, datetime




class SellerAllOrders(APIView):
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
                    "customer_name": item.order.user.username,
                    "time": item.order.created_at.strftime('%H:%M:%S'),
                    "date": item.order.created_at.strftime('%Y-%m-%d'),
                    "name": item.product.name,
                    "place": item.order.delivery_address.city,
                    "quantity": item.quantity,
                    "status": item.status,
                    "price": item.product.price
                })
            # return Response({'Status: 1', 'message': 'Success', })
            return Response({'Status': '1', 'message': 'Success', 'Data': data}, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response({'Status': '0', 'message': 'Product not found or you do not own this product.'}, status=status.HTTP_404_NOT_FOUND)
        



class SellerPendingOrders(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        user = request.user

        # Check if the user is a seller
        if user.profile.user_type != 'seller':
            return Response({'Status': '0', 'message': 'You are not authorized to view products as you are not a seller.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            # If a specific product ID is provided, fetch the product and check if it belongs to the seller
            order_items = OrderItem.objects.filter(product__vendor=user, status='0')
            data = []
            for item in order_items:
                data.append({
                    "customer_name": item.order.user.username,
                    "time": item.order.created_at.strftime('%H:%M:%S'),
                    "date": item.order.created_at.strftime('%Y-%m-%d'),
                    "name": item.product.name,
                    "place": item.order.delivery_address.city,
                    "quantity": item.quantity,
                    "status": item.status,
                    "price": item.product.price
                })
            # return Response({'Status: 1', 'message': 'Success', })
            return Response({'Status': '1', 'message': 'Success', 'Data': data}, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response({'Status': '0', 'message': 'Product not found or you do not own this product.'}, status=status.HTTP_404_NOT_FOUND)
        

    
class SellerConfirmedOrders(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        user = request.user

        # Check if the user is a seller
        if user.profile.user_type != 'seller':
            return Response({'Status': '0', 'message': 'You are not authorized to view products as you are not a seller.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            # If a specific product ID is provided, fetch the product and check if it belongs to the seller
            order_items = OrderItem.objects.filter(product__vendor=user, status='1')
            data = []
            for item in order_items:
                data.append({
                    "customer_name": item.order.user.username,
                    "time": item.order.created_at.strftime('%H:%M:%S'),
                    "date": item.order.created_at.strftime('%Y-%m-%d'),
                    "name": item.product.name,
                    "place": item.order.delivery_address.city,
                    "quantity": item.quantity,
                    "status": item.status,
                    "price": item.product.price
                })
            # return Response({'Status: 1', 'message': 'Success', })
            return Response({'Status': '1', 'message': 'Success', 'Data': data}, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response({'Status': '0', 'message': 'Product not found or you do not own this product.'}, status=status.HTTP_404_NOT_FOUND)
        



    
class SellerShippedOrders(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        user = request.user

        # Check if the user is a seller
        if user.profile.user_type != 'seller':
            return Response({'Status': '0', 'message': 'You are not authorized to view products as you are not a seller.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            # If a specific product ID is provided, fetch the product and check if it belongs to the seller
            order_items = OrderItem.objects.filter(product__vendor=user, status='2')
            data = []
            for item in order_items:
                data.append({
                    "customer_name": item.order.user.username,
                    "time": item.order.created_at.strftime('%H:%M:%S'),
                    "date": item.order.created_at.strftime('%Y-%m-%d'),
                    "name": item.product.name,
                    "place": item.order.delivery_address.city,
                    "quantity": item.quantity,
                    "status": item.status,
                    "price": item.product.price
                })
            # return Response({'Status: 1', 'message': 'Success', })
            return Response({'Status': '1', 'message': 'Success', 'Data': data}, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response({'Status': '0', 'message': 'Product not found or you do not own this product.'}, status=status.HTTP_404_NOT_FOUND)
        



class SellerDeliveredOrders(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        user = request.user

        # Check if the user is a seller
        if user.profile.user_type != 'seller':
            return Response({'Status': '0', 'message': 'You are not authorized to view products as you are not a seller.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            # If a specific product ID is provided, fetch the product and check if it belongs to the seller
            order_items = OrderItem.objects.filter(product__vendor=user, status='3')
            data = []
            for item in order_items:
                data.append({
                    "customer_name": item.order.user.username,
                    "time": item.order.created_at.strftime('%H:%M:%S'),
                    "date": item.order.created_at.strftime('%Y-%m-%d'),
                    "name": item.product.name,
                    "place": item.order.delivery_address.city,
                    "quantity": item.quantity,
                    "status": item.status,
                    "price": item.product.price
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
        
        


    


class ChangeOrderStatus(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        user=request.user
        if user.profile.user_type == "seller":
            order_number = request.data.get('order_number', None)
            product_id = request.data.get('product_id', None)
            status = request.data.get('status', None)

            if not order_number or not product_id or not status:
                return Response({
                    'Status': '0',
                    'message': 'You must provide order_number, product_id, and status'
                })
            try:
                # product_data['status'] = item.order.get_status_display()
                pending_orders = OrderItem.objects.filter(product__vendor=user, order__order_number=order_number).first()
                pending_orders.status = status
                pending_orders.save()
                send_message_to_customer(user, pending_orders)
                store_notification(user=pending_orders.order.user, heading="Order Status Changed", message=f"Your order has {pending_orders.get_status_display()} {pending_orders.order.order_number}")
                return Response({
                    'Status': '1',
                    'message': f'The status of the order has changed to {pending_orders.get_status_display()}'
                })
            except:
                return Response({
                    'Status': '0',
                    'message': 'Order not found'
                })
        else:
            return Response({'Status': '0', 'message': 'You are not a seller'})
        



class SellerRevenueSalesView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user  # Logged-in seller
        if user.profile.user_type == "seller":
            seller_orders = CustomerOrder.objects.filter(items__product__vendor=user).distinct()

            months = [
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"
            ]

            # Prepare a list of objects for each month
            graph_data = []

            for month_index, month_name in enumerate(months, start=1):
                month_orders = seller_orders.filter(created_at__month=month_index)
                revenue = month_orders.aggregate(total_revenue=Sum('items__price'))['total_revenue'] or 0
                sales = month_orders.aggregate(total_sales=Count('items__id'))['total_sales'] or 0

                graph_data.append({
                    "month": month_name,
                    "revenue": float(revenue),
                    "sales": sales
                })

            return Response({
                'Status': '1',
                'message': 'Success',
                'Data': graph_data
            })
        else:
            return Response({
                'Sttaus': '1',
                'message': "You are not a seller"
            })






class SellerSalesByYearView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user  # Logged-in seller

        if user.profile.user_type != "seller":
            return Response({
                'Status': '0',
                'message': "You are not a seller"
            }, status=status.HTTP_403_FORBIDDEN)

        # Get the year from query params
        year = request.query_params.get('year')
        if not year:
            raise ValidationError({'year': 'This query parameter is required.'})

        try:
            year = int(year)
        except ValueError:
            raise ValidationError({'year': 'Year must be a valid integer.'})

        # Filter orders by the logged-in seller and the specified year
        seller_orders = CustomerOrder.objects.filter(
            items__product__vendor=user,
            created_at__year=year
        ).distinct()

        months = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]

        # Prepare a list of objects for each month
        sales_data = []

        for month_index, month_name in enumerate(months, start=1):
            month_orders = seller_orders.filter(created_at__month=month_index)
            sales = month_orders.aggregate(total_sales=Count('items__id'))['total_sales'] or 0

            sales_data.append({
                "month": month_name,
                "sales": sales
            })

        return Response({
            'Status': '1',
            'message': 'Success',
            'Data': sales_data
        })





class SellerMonthlyRevenueView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user  # Logged-in seller
        if user.profile.user_type != "seller":
            return Response({
                'Status': '1',
                'message': "You are not a seller"
            }, status=403)

        # Get year from query params, default to the current year
        year_param = request.query_params.get('year', datetime.now().year)
        try:
            year = int(year_param)  # Validate year as an integer
        except ValueError:
            return Response({
                'Status': '0',
                'message': "Invalid year provided"
            }, status=400)

        # Filter orders for the seller within the specific year
        seller_orders = CustomerOrder.objects.filter(
            items__product__vendor=user,
            created_at__year=year
        ).distinct()

        months = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]

        # Prepare a list of revenue data for each month
        graph_data = []
        for month_index, month_name in enumerate(months, start=1):
            month_orders = seller_orders.filter(created_at__month=month_index)
            revenue = month_orders.aggregate(
                total_revenue=Sum('items__price')
            )['total_revenue'] or 0

            graph_data.append({
                "month": month_name,
                "revenue": float(revenue)
            })

        return Response({
            'Status': '1',
            'message': 'Success',
            'Data': graph_data
        }, status=200)