
from django.views.decorators.csrf import csrf_exempt

from django.utils.decorators import method_decorator

from products.models import Productimg
from products.serializers import ProductSerializer

from accounts.models import Profile





from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from rest_framework import status
from ..models import Product, Cart, CartItem, OrderProductImage
from ..models import CustomerOrder, OrderItem
from ..serializers import CustomerOrderSerializer
from django.utils.crypto import get_random_string




from rest_framework.authentication import TokenAuthentication












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
        user = request.user  # Assuming the user is authenticated

        full_cart = get_cart_item(request)
        print("dsdsd", full_cart['delivery_charge'])
        profile = Profile.objects.get(user=user)
        delivery_address = profile.default_address

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
                total_price= full_cart['offer_price'],  # Set any dummy price or calculate from cart
                delivery_charge= full_cart['delivery_charge'],  # Dummy delivery charge
                net_total= full_cart['total_price'],  # Total price + delivery charge
                payment_type='COD',  # Dummy payment type
                order_number=order_number,
                delivery_address=delivery_address,
                payment_status='Pending'
            )

            # Create Order Items with images
            products = Product.objects.all()  # Fetch some products (you can change logic here)

            for item in cart_items:
                # quantity = item.quantity  # Example quantity
                order_item = OrderItem.objects.create(
                    order=order,
                    status='1',
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price,  # Use product price or custom price
                )

                # Example logic to associate images (you can modify this as needed)
                for img in item.product.product_images.all():  # Assuming you have a related_name 'images' in the Product model
                    OrderProductImage.objects.create(
                        order_item=order_item,
                        image=img.image  # Use the image from the product's images
                    )
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
            # product_data['status'] = item.order.get_status_display()
            product_data['order_status'] = item.status
            product_data['is_approved'] = item.is_approved
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
            product_data['payment_type'] = item.order.payment_type

            response_data.append(product_data)

        return Response({
            'Status': '1',
            'message': 'Products retrieved successfully',
            'Data': response_data
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
        order_items = OrderItem.objects.filter(order__in=orders, is_approved=False)

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
            product_data['is_approved'] = item.is_approved
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
            product_data['payment_type'] = item.order.payment_type

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
        order_items = OrderItem.objects.filter(order__in=orders, status="2", is_approved=True)
        print("ppppp", order_items)

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
            product_data['is_approved'] = item.is_approved
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
            product_data['payment_type'] = item.order.payment_type

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




