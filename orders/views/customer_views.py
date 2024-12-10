from django.utils.crypto import get_random_string
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404

from asgiref.sync import async_to_sync


from orders.models import *
from orders.serializers import *
from products.models import Product, Productimg, Wishlist, WishlistItem
from products.serializers import ProductSerializer
from accounts.models import Profile
from accounts.consumers import store_notification, send_message

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import TokenAuthentication
from rest_framework import status

from channels.layers import get_channel_layer






class Checkout(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    def get(self, request):
        user = request.user

        user = request.user

        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            return Response({'Status': '0', 'message': 'No items in the cart'}, status=status.HTTP_404_NOT_FOUND)

        cart_items = CartItem.objects.filter(cart=cart)
        data = []
        total_delivery_charge = []
        total_price = []
        actual_price = []
        offer_price = []
        for item in cart_items:
            product_images = Productimg.objects.filter(product=item.product).values_list('image', flat=True)  # Get all product images
            product_image = product_images[0] if product_images else None
            total_delivery_charge.append(item.product.delivery_charge if item.quantity < item.product.min_order_quantity else 0)
            total_price.append(item.product.price * item.quantity)
            actual_price.append(item.product.actual_price * item.quantity)
            offer_price.append(item.product.price * item.quantity)
            data.append({
                "id": item.product.id,
                "name": item.product.name,
                "price": item.product.price,
                'product_images': f'/media/{product_image}' if product_image != None else None,
                'quantity': item.quantity,
                "offer_percent": item.product.offer_percent,
                "actual_price": item.product.actual_price,
                "delivery_charge": item.product.delivery_charge
            })
        return Response({"Status": "1", "message": "Success", "Data": data, "delivery_charge": 0.0 if sum(total_delivery_charge) == 0 else sum(total_delivery_charge), "actual_prices": sum(actual_price), "offer_price": sum(offer_price), "total_price": sum(total_price) + sum(total_delivery_charge)}, status=status.HTTP_200_OK)
    



def get_cart_item(request):
        user = request.user

        user = request.user

        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            return Response({'Status': '0', 'message': 'No items in the cart'}, status=status.HTTP_404_NOT_FOUND)

        cart_items = CartItem.objects.filter(cart=cart)
        data = []
        total_delivery_charge = []
        total_price = []
        actual_price = []
        offer_price = []
        for item in cart_items:
            product_images = Productimg.objects.filter(product=item.product).values_list('image', flat=True)  # Get all product images
            product_image = product_images[0] if product_images else None
            total_delivery_charge.append(item.product.delivery_charge if item.quantity < item.product.min_order_quantity else 0)
            total_price.append(item.product.price * item.quantity)
            actual_price.append(item.product.actual_price * item.quantity)
            offer_price.append(item.product.price * item.quantity)
            data.append({
                "id": item.product.id,
                "name": item.product.name,
                "price": item.product.price,
                'product_images': product_image,
                'quantity': item.quantity,
                "offer_percent": item.product.offer_percent,
                "actual_price": item.product.actual_price,
                "delivery_charge": item.product.delivery_charge
            })
        return {"delivery_charge": sum(total_delivery_charge), "actual_prices": sum(actual_price), "offer_price": sum(offer_price), "total_price": sum(total_price) + sum(total_delivery_charge)}




class PlaceOrderView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    def post(self, request, format=None):
        user = request.user

        full_cart = get_cart_item(request)
        profile = Profile.objects.get(user=user)
        delivery_address = profile.default_address
        if not delivery_address:
            try:
                delivery_address = DeliveryAddress.objects.filter(user=user).first()
            except:
                return Response({"Status": "0", "message": "You have to add delivery address"})

        try:
            cart = Cart.objects.get(user=user)
            cart_items = CartItem.objects.filter(cart=cart)
        except:
            return Response({"Status": "0", "message": "No cart Found"})
        
        if cart_items:
        
            # Generate a unique order number
            order_number = get_random_string(length=15)

            # Creating the order
            order = CustomerOrder.objects.create(
                user=user,
                # status='1',  # Ordered
                total_price= full_cart['offer_price'], # Calculate from cart
                delivery_charge= full_cart['delivery_charge'],
                net_total= full_cart['total_price'],  # Total price + delivery charge
                order_number=order_number,
                delivery_address=delivery_address,
            )

            # Create Order Items with images
            # products = Product.objects.all()  # Fetch some products (you can change logic here)

            for item in cart_items:
                # quantity = item.quantity  # Example quantity
                order_item = OrderItem.objects.create(
                    order=order,
                    status='0',
                    payment_type='COD',
                    product=item.product,
                    quantity=item.quantity,
                    payment_status='Pending',
                    price=item.product.price,  # Use product price or custom price
                )

                # Example logic to associate images (you can modify this as needed)
                for img in item.product.product_images.all():  # Assuming you have a related_name 'images' in the Product model
                    OrderProductImage.objects.create(
                        order_item=order_item,
                        image=img.image  # Use the image from the product's images
                    )
                send_message(item, order)
                store_notification(user=item.product.vendor, heading="You have a new order", message=f"New order placed with ID {order.order_number}")
            cart_items.delete()
            
            
            
            # Serialize and return the order
            serializer = CustomerOrderSerializer(order)
            return Response({"Status": "1", "message": "Success", "Data": serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response({"Status": "0", "message": "No items in the cart"})







class AllOrdersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Get all the orders of the logged-in user
        orders = CustomerOrder.objects.filter(user=user)

        if not orders.exists():
            return Response({
                'Status': '0',
                'message': 'No orders found for this user',
                'Data': []
            }, status=status.HTTP_404_NOT_FOUND)

        # Get all the order items related to the user's orders
        order_items = OrderItem.objects.filter(order__in=orders)

        if not order_items.exists():
            return Response({
                'Status': '0',
                'message': 'No products found for this user',
                'Data': []
            }, status=status.HTTP_404_NOT_FOUND)

        # Prepare response data
        response_data = []
        for item in order_items:
            product_data = ProductSerializer(item.product).data
            product_data['order_number'] = item.order.order_number
            product_data['order_status'] = item.status
            product_data['delivery_from'] = item.product.vendor.profile.address if item.product.vendor else "Unknown"
            product_data['delivery_to'] = item.order.delivery_address.city if item.order.delivery_address else "Unknown"
            product_data['delivery_date'] = item.estimated_delivery_date().strftime("%d %b %Y")
            product_data['quantity'] = item.quantity
            product_data['address'] = [{"name": item.order.delivery_address.name,
                                       "house_name": item.order.delivery_address.housename,
                                       "city": item.order.delivery_address.city,
                                       "state": item.order.delivery_address.state,
                                       "pincode": item.order.delivery_address.pincode,
                                       "mobile_number": item.order.delivery_address.mobile}]
            delivery_charge = item.product.delivery_charge if item.quantity < item.product.min_order_quantity else 0
            product_data['subtotal'] = item.quantity * item.price + delivery_charge
            product_data['payment_type'] = item.payment_type

            response_data.append(product_data)

        return Response({
            'Status': '1',
            'message': 'Products retrieved successfully',
            'Data': response_data
        }, status=status.HTTP_200_OK)
    


class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_number, product_id):
        user = request.user


        try:
            # Get all the orders of the logged-in user
            order = CustomerOrder.objects.get(user=user, order_number=order_number)
            product = Product.objects.get(id=product_id)

        except:
            return Response({
                'Status': '0',
                'message': 'No orders found for this user',
                'Data': []
            }, status=status.HTTP_404_NOT_FOUND)

        try:
            # Get all the order items related to the user's orders
            order_item = OrderItem.objects.get(order=order, product=product)

        except:
            return Response({
                'Status': '0',
                'message': 'No products found for this user',
                'Data': []
            }, status=status.HTTP_404_NOT_FOUND)

        # Prepare response data
        response_data = []
        # for item in order_item:
        product_data = ProductSerializer(order_item.product).data
        product_data['order_number'] = order_item.order.order_number
        product_data['order_status'] = order_item.status
        product_data['delivery_from'] = order_item.product.vendor.profile.address if order_item.product.vendor else "Unknown"
        product_data['delivery_to'] = order_item.order.delivery_address.city if order_item.order.delivery_address else "Unknown"
        product_data['delivery_date'] = order_item.estimated_delivery_date().strftime("%d %b %Y")
        product_data['quantity'] = order_item.quantity
        product_data['address'] = [{"name": order_item.order.delivery_address.name,
                                    "house_name": order_item.order.delivery_address.housename,
                                    "city": order_item.order.delivery_address.city,
                                    "state": order_item.order.delivery_address.state,
                                    "pincode": order_item.order.delivery_address.pincode,
                                    "mobile_number": order_item.order.delivery_address.mobile}]
        delivery_charge = order_item.product.delivery_charge if order_item.quantity < order_item.product.min_order_quantity else 0
        product_data['subtotal'] = order_item.quantity * order_item.price + delivery_charge
        product_data['payment_type'] = order_item.payment_type

        response_data.append(product_data)

        return Response({
            'Status': '1',
            'message': 'Products retrieved successfully',
            'Data': response_data
        }, status=status.HTTP_200_OK)
    


class CancelSingleProductOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_number, product_id):
        user = request.user

        # Get all the orders of the logged-in user
        try:
            order = CustomerOrder.objects.get(user=user, order_number=order_number)
            product = Product.objects.get(id=product_id)

        except:
            return Response({
                'Status': '0',
                'message': 'No orders found for this user',
                'Data': []
            }, status=status.HTTP_404_NOT_FOUND)

        # Get all the order items related to the user's orders
        try:
            order_item = OrderItem.objects.get(order=order, product=product, status='0')

        except:
            return Response({
                'Status': '0',
                'message': 'No products found for this user',
                'Data': []
            }, status=status.HTTP_404_NOT_FOUND)

        order_item.status = '4'
        order_item.save()

        return Response({
            'Status': '1',
            'message': 'Order Cancelled Successfully'
        }, status=status.HTTP_200_OK)
    



class PendingOrdersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Get all the orders of the logged-in user
        orders = CustomerOrder.objects.filter(user=user)

        if not orders.exists():
            return Response({
                'Status': '1',
                'message': 'No delivered orders found for this user',
                'Data': []
            }, status=status.HTTP_200_OK)

        # Get all the order items related to the user's orders
        order_items = OrderItem.objects.filter(order__in=orders, status="0")

        if not order_items.exists():
            return Response({
                'Status': '1',
                'message': 'No products found for this user',
                'Data': []
            }, status=status.HTTP_200_OK)

        # Prepare response data
        response_data = []
        for item in order_items:
            product_data = ProductSerializer(item.product).data
            product_data['order_number'] = item.order.order_number
            product_data['order_status'] = item.status
            product_data['delivery_from'] = item.product.vendor.profile.address if item.product.vendor else "Unknown"
            product_data['delivery_to'] = item.order.delivery_address.city if item.order.delivery_address else "Unknown"
            product_data['delivery_date'] = item.estimated_delivery_date().strftime("%d %b %Y")
            product_data['quantity'] = item.quantity
            product_data['address'] = [{"name": item.order.delivery_address.name,
                                       "house_name": item.order.delivery_address.housename,
                                       "city": item.order.delivery_address.city,
                                       "state": item.order.delivery_address.state,
                                       "pincode": item.order.delivery_address.pincode,
                                       "mobile_number": item.order.delivery_address.mobile}]
            delivery_charge = item.product.delivery_charge if item.quantity < item.product.min_order_quantity else 0
            product_data['subtotal'] = item.quantity * item.price + delivery_charge
            product_data['payment_type'] = item.payment_type

            response_data.append(product_data)

        return Response({
            'Status': '1',
            'message': 'Products retrieved successfully',
            'Data': response_data
        }, status=status.HTTP_200_OK)
    

class DeliveredOrdersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Get all the orders of the logged-in user
        orders = CustomerOrder.objects.filter(user=user)

        if not orders.exists():
            return Response({
                'Status': '1',
                'message': 'No delivered orders found for this user',
                'Data': []
            }, status=status.HTTP_200_OK)

        # Get all the order items related to the user's orders
        order_items = OrderItem.objects.filter(order__in=orders, status="3")

        if not order_items.exists():
            return Response({
                'Status': '1',
                'message': 'No products found for this user',
                'Data': []
            }, status=status.HTTP_200_OK)

        # Prepare response data
        response_data = []
        for item in order_items:
            product_data = ProductSerializer(item.product).data
            product_data['order_number'] = item.order.order_number
            product_data['order_status'] = item.status
            # product_data['is_approved'] = item.is_approved
            product_data['delivery_from'] = item.product.vendor.profile.address if item.product.vendor else "Unknown"
            product_data['delivery_to'] = item.order.delivery_address.city if item.order.delivery_address else "Unknown"
            product_data['delivery_date'] = item.estimated_delivery_date().strftime("%d %b %Y")
            product_data['quantity'] = item.quantity
            product_data['address'] = [{"name": item.order.delivery_address.name if item.order.delivery_address.name else None,
                                       "house_name": item.order.delivery_address.housename,
                                       "city": item.order.delivery_address.city,
                                       "state": item.order.delivery_address.state,
                                       "pincode": item.order.delivery_address.pincode,
                                       "mobile_number": item.order.delivery_address.mobile}]
            delivery_charge = item.product.delivery_charge if item.quantity < item.product.min_order_quantity else 0
            product_data['subtotal'] = item.quantity * item.price + delivery_charge
            product_data['payment_type'] = item.payment_type

            response_data.append(product_data)

        return Response({
            'Status': '1',
            'message': 'Products retrieved successfully',
            'Data': response_data
        }, status=status.HTTP_200_OK)







@method_decorator(csrf_exempt, name='dispatch')
class CartView(APIView):
    permission_classes = [AllowAny]  # Allow access to unauthenticated users

    def get(self, request):
        user = request.user if request.user.is_authenticated else None
        session_id = request.headers.get('Session-Id', None)
        # Check if the session is initialized
        if not session_id:
            if not request.session.session_key:
                request.session['initialized'] = True  # Initialize the session
                request.session.save()  # Save to create a session ID
            session_id = request.session.session_key

        cart = Cart.objects.filter(user=user).first() if user else Cart.objects.filter(session_id=session_id).first()

        if not cart:
            return Response({'Status': '0', 'message': 'Cart not found'}, status=status.HTTP_200_OK)

        cart_items = CartItem.objects.filter(cart=cart)

        # Prepare the cart items data
        items = []
        for item in cart_items:
            product_images = Productimg.objects.filter(product=item.product).values_list('image', flat=True)
            product_image = product_images[0] if product_images else None
            items.append({
                'product_id': item.product.id,
                'product_name': item.product.name,
                'product_images': f"/media/{product_image}" if product_image else None,
                'minimum_order_quantity': item.product.min_order_quantity, 
                'quantity': item.quantity,
                'price_per_item': item.product.price,
                'total_price': item.quantity * item.product.price,
            })

        return Response({
            'Status': '1',
            'cart_id': cart.id,
            'total_items': len(items),
            'items': items,
        }, status=status.HTTP_200_OK)

    def post(self, request):
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity')
        

        if not product_id or not quantity:
            return Response({'Status': '0', 'message': 'Product ID and quantity are required'}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user if request.user.is_authenticated else None

        session_id = request.headers.get('Session-Id', None)
        if not session_id:
            if not request.session.session_key:
                request.session['initialized'] = True
                request.session.save()
            session_id = request.session.session_key
        # if user.profile.user_type == "customer":
            cart, created = Cart.objects.get_or_create(user=user) if user else Cart.objects.get_or_create(session_id=session_id)

            # Retrieve the product
            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return Response({'Status': '0', 'message': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

            # if product.stock < quantity:
            #     return Response({'Status': '0', 'message': 'Insufficient stock'}, status=status.HTTP_400_BAD_REQUEST)

            cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

            if created:
                cart_item.quantity = quantity
            else:
                # if cart_item.quantity + quantity > product.stock:
                    # return Response({'Status': '0', 'message': 'Insufficient stock'}, status=status.HTTP_400_BAD_REQUEST)
                cart_item.quantity += quantity

            cart_item.save()

            return Response({"Status": "1", "message": "Product added to cart successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"Status": "1", "message": "You must signup as a customer to use the cart and to place order"})

    def delete(self, request):
        product_id = request.data.get('product_id')

        if not product_id:
            return Response({'Status': '0', 'message': 'Product ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user if request.user.is_authenticated else None
        
        session_id = request.headers.get('Session-Id', None)
        if not session_id:
            session_id = request.session.session_key
        cart = Cart.objects.filter(user=user).first() if user else Cart.objects.filter(session_id=session_id).first()

        if not cart:
            return Response({'Status': '0', 'message': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
        except CartItem.DoesNotExist:
            return Response({'Status': '0', 'message': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)

        cart_item.delete()

        return Response({"Status": "1", "message": "Item removed from cart successfully"}, status=status.HTTP_200_OK)

    






class UpdateCart(APIView):
    # Remove permission_classes for unauthenticated access
    def post(self, request):
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity')

        if not product_id or not quantity:
            return Response({'Status': '0', 'message': 'Product ID and quantity are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'Status': '0', 'message': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if user is authenticated
        user = request.user if request.user.is_authenticated else None

        # If authenticated, get the cart by user
        if user:
            try:
                cart = Cart.objects.get(user=user)
            except Cart.DoesNotExist:
                return Response({'Status': '0', 'message': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            # If not authenticated, get the cart by session ID
            session_id = request.headers.get('Session-Id', None)
            if not session_id:
                session_id = request.session.session_key
            cart = Cart.objects.filter(session_id=session_id).first()
            if not cart:
                return Response({'Status': '0', 'message': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check for existing cart item
        try:
            cart_item = CartItem.objects.get(cart=cart, product=product)
        except CartItem.DoesNotExist:
            return Response({'Status': '0', 'message': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)

        # Validate stock availability
        # if product.stock + cart_item.quantity < int(quantity):
            # return Response({'Status': '0', 'message': 'Insufficient stock'}, status=status.HTTP_400_BAD_REQUEST)

        # Adjust the stock
        # product.stock += cart_item.quantity - int(quantity)
        # product.save()

        # Update the cart item quantity
        cart_item.quantity = int(quantity)
        cart_item.save()

        # Prepare response data
        serializer = ProductSerializer(product)
        product_data = serializer.data
        product_data['quantity'] = cart_item.quantity

        if cart_item.quantity < product.min_order_quantity:
            delivery_charge = product.delivery_charge
            return Response({
                "Status": "1",
                "message": "Cart updated successfully",
                "delivery_charge": delivery_charge,
                "info": f"You need to pay a delivery charge of {delivery_charge} as the quantity is less than the minimum order quantity.",
                "Data": [product_data]
            }, status=status.HTTP_200_OK)
        
        # If no delivery charge
        return Response({
            "Status": "1",
            "message": "Cart updated successfully",
            "delivery_charge": 0.0,
            "Data": [product_data]
        }, status=status.HTTP_200_OK)






@method_decorator(csrf_exempt, name='dispatch')
class CartFromWishlistView(APIView):
    permission_classes = [AllowAny] 
    def post(self, request):
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity')
        

        if not product_id or not quantity:
            return Response({'Status': '0', 'message': 'Product ID and quantity are required'}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user if request.user.is_authenticated else None

        session_id = request.headers.get('Session-Id', None)
        if not session_id:
            if not request.session.session_key:
                request.session['initialized'] = True
                request.session.save()
            session_id = request.session.session_key
        cart, created = Cart.objects.get_or_create(user=user) if user else Cart.objects.get_or_create(session_id=session_id)


        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'Status': '0', 'message': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

    
        try:
            wishlist = Wishlist.objects.get(user=user) if user else Wishlist.objects.get(session_id=session_id)
            try:
                wishlist_item = WishlistItem.objects.get(wishlist=wishlist, product=product_id)
                cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
                if created:
                    cart_item.quantity = quantity
                else:
                    cart_item.quantity += quantity

                cart_item.save()
                wishlist_item.delete()
                # wishlist.delete()

                return Response({"Status": "1", "message": "Product moved to cart succesfully"}, status=status.HTTP_201_CREATED)
            except:
                return Response({"Status": '0', "message": "Product not found in wishlist"})
        except:
            return Response({"Status": '0', "message": "No wishlist found"})







