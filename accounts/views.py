from django.shortcuts import render, redirect
from .forms import UserCreationForm, LoginForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from orders.models import Order, OrderDetails
from django.views.generic import View, TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404 
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from django.contrib.auth.models import User
import json
from django.http import HttpResponseRedirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import Profile
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.core.exceptions import ObjectDoesNotExist
from PIL import Image
from django.conf import settings
from wsgiref.util import FileWrapper
# Import mimetypes module
import mimetypes
# import os module
import os
# Import HttpResponse module
from django.http.response import HttpResponse

# Create your views here.
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Category, Subcategory, RatingReview
from .serializers import CategorySerializer,RatingReviewSerializer
from rest_framework import status
from .models import Banner, Brand, Product, Productimg, Cart, CartItem
from .serializers import BannerSerializer, BrandSerializer, OfferProductSerializer, ProductSerializer, ProductimgSerializer,CartSerializer, CartItemSerializer
from django.shortcuts import get_object_or_404


class RegisterView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            email = data.get('email')
            name = data.get('Name')
            phone = data.get('Phone')
            user_type = data.get('Type')
            gst = data.get('Gst')
            shopname = data.get('Shopname')
            logoimage = data.get('Logoimage')
            company_name = data.get('Company name')
            latitude = data.get('Latitude')
            longitude = data.get('longitude')
            password = data.get('Password')

            if not email or not password:
                return Response({'Status': '0', 'message': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)

            if User.objects.filter(email=email).exists():
                return Response({'Status': '0', 'message': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

            # Create user
            new_user = User.objects.create_user(username=email, email=email, password=password)
            new_user.first_name = name
            new_user.save()

            # Create or update profile
            profile, created = Profile.objects.get_or_create(user=new_user)
            profile.email = email
            profile.name = name
            profile.phone = phone
            profile.type = user_type
            profile.gst = gst
            profile.shopname = shopname
            profile.company_name = company_name
            profile.latitude = latitude
            profile.longitude = longitude
            profile.status = 'vendor' if user_type.lower() == 'seller' else 'customer'
            profile.save()

            # Handle logoimage (you might want to use a file upload handler here)
            # For now, we're just storing the string, which isn't ideal for images
            if logoimage:
                profile.logoimage = logoimage
                profile.save()

            return Response({
                'Status': '1',
                'message': 'Success',
                'Data': {
                    'name': profile.name,
                    'Mobile': profile.phone,
                    'userid': new_user.id,
                    'Type': profile.type
                }
            }, status=status.HTTP_201_CREATED)

        except json.JSONDecodeError:
            return Response({'Status': '0', 'message': 'Invalid JSON'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'Status': '0', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            email = data.get('email')
            password = data.get('Password')

            if not email or not password:
                return Response({'Status': '0', 'message': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                user = User.objects.get(email=email)
                user = authenticate(request, username=user.username, password=password)
            except User.DoesNotExist:
                return Response({'Status': '0', 'message': 'Invalid email or password'}, status=status.HTTP_400_BAD_REQUEST)

            if user is not None:
                login(request, user)
                profile = Profile.objects.get(user=user)
                return Response({
                    'Status': '1',
                    'message': 'Success',
                    'Data': {
                        'name': profile.name,
                        'Mobile': profile.phone,
                        'userid': user.id,
                        'Type': profile.type
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response({'Status': '0', 'message': 'Invalid email or password'}, status=status.HTTP_400_BAD_REQUEST)

        except json.JSONDecodeError:
            return Response({'Status': '0', 'message': 'Invalid JSON'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'Status': '0', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


def logout_user(request):
    logout(request)
    messages.success(
        request, 'Your Now Logout !')
    return redirect('accounts:login')


def dashboard_customer(request):
    if not request.user.is_authenticated and request.user.is_anonymous:
        return redirect('accounts:login')
    context = None
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        display_name = request.POST['display_name']
        bio = request.POST['bio']
        mobile_number = request.POST['mobile_number']
        city = request.POST['city']
        address = request.POST['address']
        post_code = request.POST['post_code']
        country = request.POST['country']
        state = request.POST['state']
        user = User.objects.get(username=request.user)
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        profile = Profile.objects.get(user=request.user)
        try:
            image = request.FILES["image"]

        except:
            image = None

        if image:
            profile.image = image
        profile.display_name = display_name
        profile.bio = bio
        profile.mobile_number = mobile_number
        profile.city = city
        profile.address = address
        profile.post_code = post_code
        profile.country = country
        profile.state = state
        profile.save()
        messages.success(
            request, 'Your Profile Info Has Been Saved !')
        return redirect("accounts:dashboard_customer")

    else:
        profile = Profile.objects.get(
            user=request.user)
        print(profile)
        context = {
            "profile": profile,
        }
    return render(request, 'accounts/page-account.html', context)



def dashboard_account_details(request):
    if not request.user.is_authenticated and request.user.is_anonymous:
        return redirect('accounts:login')
    context = None
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        display_name = request.POST['display_name']
        bio = request.POST['bio']
        mobile_number = request.POST['mobile_number']
        city = request.POST['city']
        address = request.POST['address']
        post_code = request.POST['post_code']
        country = request.POST['country']
        state = request.POST['state']
        user = User.objects.get(username=request.user)
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        profile = Profile.objects.get(user=request.user)
        try:
            image = request.FILES["image"]

        except:
            image = None

        if image:
            profile.image = image

        if image:
            try:
                Image.open(image)

            except:
                messages.warning(request, 'sorry, your image is invalid')
                return redirect("accounts:account_details")
        profile.display_name = display_name
        profile.bio = bio
        profile.mobile_number = mobile_number
        profile.city = city
        profile.address = address
        profile.post_code = post_code
        profile.country = country
        profile.state = state
        profile.save()
        messages.success(
            request, 'Your Profile Info Has Been Saved !')
        return redirect("accounts:account_details")

    else:
        profile = Profile.objects.get(
            user=request.user)
        print(profile)
        context = {
            "profile": profile,
        }
    return render(request, 'accounts/account-details.html', context)


def order_tracking(request):

    return render(request, 'accounts/order-tracking.html')


@login_required(login_url='accounts:login')
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            login(request, request.user)
            messages.success(
                request, 'Password successfully changed!')
            return redirect('accounts:change_password')

        else:
            messages.warning(request, 'Please fix the error below.')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, "accounts/change-password.html",  {
        'form': form,

        'title': 'Change Password',
    }

    )


class MyOrdersJsonListView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):

        upper = int(self.request.GET.get("num_products"))
        lower = upper - 10
        orders = list(Order.objects.all().filter(
            user=self.request.user).values().order_by("-order_date")[lower:upper])
        orders_size = len(Order.objects.all().filter(user=self.request.user))
        max_size = True if upper >= orders_size else False
        return JsonResponse({"data": orders,  "max": max_size, "orders_size": orders_size, }, safe=False)


def order(request, order_id):
    if not request.user.is_authenticated and request.user.is_anonymous:
        return redirect('accounts:login')
    context = None
    if request.user.is_authenticated and not request.user.is_anonymous:
        if Order.objects.all().filter(id=order_id, user=request.user, is_finished=True):
            order = Order.objects.get(id=order_id, user=request.user)
            order_details = OrderDetails.objects.all().filter(order=order)
            total = 0
            for sub in order_details:
                total += sub.price * sub.quantity
            context = {
                "order": order,
                "order_details": order_details,
                "total": total,
            }
        elif Order.objects.all().filter(id=order_id, user=request.user, is_finished=False):
            return redirect('orders:cart')
        else:
            messages.warning(
                request, "You don't have access to this page !")
            return redirect('accounts:dashboard_customer')
    return render(request, "accounts/order-archive.html", context)


@login_required(login_url='accounts:login')
def download_list(request):
    order_list = Order.objects.all().filter(
        user=request.user, is_finished=True).order_by("-order_date")
    files = {}
    for order in order_list:
        print(order.id)
        order_details = OrderDetails.objects.all().filter(order=order)
        for file in order_details:
            if file.product.digital_file:
                files[int(order.id)] = str(
                    file.product.digital_file.name.split('/')[-1])
        print(files)
    context = {
        "files": files,
    }
    return render(request, 'accounts/download-page.html', context)


@login_required(login_url='accounts:login')
def download_file(request, order_id, filename):
    if request.user.is_authenticated and not request.user.is_anonymous:
        if Order.objects.all().filter(id=order_id, user=request.user, is_finished=True):
            # Define Django project base directory
            # BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            BASE_DIR = settings.MEDIA_ROOT
            # Define the full file path
            filepath = BASE_DIR + '/products/files/' + filename
            # filepath = os.path.join(settings.MEDIA_ROOT, filename)
            print(filepath)
            # Open the file for reading content
            # path = open(filepath, 'rb')
            path = FileWrapper(open(filepath, 'rb'))
            # Set the mime type
            mime_type, _ = mimetypes.guess_type(filepath)
            # Set the return value of the HttpResponse
            response = HttpResponse(path, content_type=mime_type)
            # Set the HTTP header for sending to browser
            response['Content-Disposition'] = f"attachment; filename={filename}"
            # Return the response value
            return response

        elif Order.objects.all().filter(id=order_id, user=request.user, is_finished=False):
            return redirect('orders:cart')
        else:
            messages.warning(
                request, "You don't have access to this page !")
            return redirect('accounts:dashboard_customer')

# class CategoryListView(APIView):
#     def get(self, request, format=None):
#         categories = Category.objects.all()
#         serializer = CategorySerializer(categories, many=True)
#         return Response({
#             "Status": "1",
#             "message": "Success",
#             "Data": serializer.data
#         })
        
#     def post(self, request, format=None):
#         serializer = CategorySerializer(data=request.data)
#         if serializer.is_valid():
#             category = Category.objects.create(
#                 name=serializer.validated_data['categoryname'],
#                 image=serializer.validated_data.get('image', '')
#             )
#             for subcategory_data in serializer.validated_data['subcategories']:
#                 Subcategory.objects.create(
#                     category=category,
#                     name=subcategory_data['subcategoryname'],
#                     image=subcategory_data.get('image', '')
#                 )
#             return Response({
#                 "Status": "1",
#                 "message": "Category created successfully",
#                 "Data": serializer.data
#             }, status=status.HTTP_201_CREATED)
#         return Response({
#             "Status": "0",
#             "message": "Error",
#             "Data": serializer.errors
#         }, status=status.HTTP_400_BAD_REQUEST)

class BannerListView(APIView):
    def get(self, request, format=None):
        print("check")
        banners = Banner.objects.all()
        serializer = BannerSerializer(banners, many=True)
        return Response({
            "Status": "1",
            "message": "Success",
            "Data": serializer.data
        })        
        
    def post(self, request, format=None):
        serializer = BannerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "Status": "1",
                "message": "Banner added successfully",
                "Data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "Status": "0",
            "message": "Error",
            "Errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)    
        
class AddBrandView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    def post(self, request, format=None):
        serializer = BrandSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "Status": "1",
                "message": "Brand added successfully",
                "Data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "Status": "0",
            "message": "Failed to add brand",
            "Errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    # parser_classes = (MultiPartParser, FormParser)
    # def post(self, request, format=None):
    #         brand_id = request.data.get('id')
    #         if not brand_id:
    #             return Response({
    #                 "Status": "0",
    #                 "message": "Failed to add brand",
    #                 "Errors": {"id": ["This field is required."]}
    #             }, status=status.HTTP_400_BAD_REQUEST)
            
    #         try:
    #             brand = Brand.objects.get(id=brand_id)
    #             serializer = BrandSerializer(brand, data=request.data)
    #         except Brand.DoesNotExist:
    #             serializer = BrandSerializer(data=request.data)
            
    #         if serializer.is_valid():
    #             serializer.save()
    #             return Response({
    #                 "Status": "1",
    #                 "message": "Brand added successfully",
    #                 "Data": serializer.data
    #             }, status=status.HTTP_201_CREATED)
            
    #         return Response({
    #             "Status": "0",
    #             "message": "Failed to add brand",
    #             "Errors": serializer.errors
    #         }, status=status.HTTP_400_BAD_REQUEST)            
                
class TrendingBrandsView(APIView):
    def get(self, request, format=None):
        brands = Brand.objects.all()
        serializer = BrandSerializer(brands, many=True)
        return Response({
            "Status": "1",
            "message": "Success",
            "Data": serializer.data}
        , status=status.HTTP_200_OK)        

class OfferProductView(APIView):
    def get(self, request, format=None):
        products = Product.objects.filter(offer_percent__gt=0)
        serializer = OfferProductSerializer(products, many=True)
        return Response({
            "Status": "1",
            "message": "Success",
            "Data": serializer.data
        })        
        

# class ProductDetailView(APIView):
#     def post(self, request, format=None):
#         product_id = request.data.get('product_id')
#         try:
#             product = Product.objects.get(id=product_id)
#         except Product.DoesNotExist:
#             return Response({
#                 "Status": "0",
#                 "message": "Product not found"
#             }, status=status.HTTP_404_NOT_FOUND)

#         serializer = ProductDetailSerializer(product)
#         return Response({
#             "Status": "1",
#             "message": "Success",
#             "Data": [serializer.data]
#         })        
class ProductDetail(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, product_id=None):
        try:
            if product_id is not None:
                product = Product.objects.get(id=product_id)
                serializer = ProductSerializer(product)
                return Response({'Status': '1', 'message': 'Success', 'Data': serializer.data}, status=status.HTTP_200_OK)
            else:
                products = Product.objects.all()
                serializer = ProductSerializer(products, many=True)
                return Response({'Status': '1', 'message': 'Success', 'Data': serializer.data}, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response({'Status': '0', 'message': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        product_serializer = ProductSerializer(data=request.data,  context={'request': request})
        if product_serializer.is_valid():
            product = product_serializer.save()
            images_data = request.FILES.getlist('images')
            for image_data in images_data:
                Productimg.objects.create(product=product, image=image_data)
            return Response({"Status": "1", "message": "Product added successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"Status": "0", "message": "Failed to add product", "Errors": product_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        

@method_decorator(csrf_exempt, name='dispatch')
class CategoryCreateView(APIView):
    def post(self, request, format=None):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "Status": "1",
                "message": "Category added successfully",
                "Data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "Status": "0",
            "message": "Failed to add category",
            "Errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class CategoryListView(APIView):
    def get(self, request, format=None):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response({
            "Status": "1",
            "message": "Success",
            "Data": serializer.data
        }, status=status.HTTP_200_OK)        
        
        
class ProductSearchView(APIView):
    
    def post(self, request):
        search_word = request.data.get('search_word', '')
        if search_word:
            products = Product.objects.filter(name__icontains=search_word)
            serializer = ProductSerializer(products, many=True)
            return Response({'Status': '1', 'message': 'Success', 'Data': serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({'Status': '0', 'message': 'Search word not provided'}, status=status.HTTP_400_BAD_REQUEST)
        
class RatingReviewListCreate(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        reviews = RatingReview.objects.all()
        serializer = RatingReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = RatingReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RatingReviewDetail(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return RatingReview.objects.get(pk=pk)
        except RatingReview.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        review = self.get_object(pk)
        serializer = RatingReviewSerializer(review)
        return Response(serializer.data)

    def put(self, request, pk):
        review = self.get_object(pk)
        serializer = RatingReviewSerializer(review, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        review = self.get_object(pk)
        serializer = RatingReviewSerializer(review, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        review = self.get_object(pk)
        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    
class AddToCart(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        product_id = request.data.get('productid')
        quantity = request.data.get('quantity')

        # Debugging print statements
        print(f"Request data: Product ID = {product_id}, Quantity = {quantity}")

        if not product_id or not quantity:
            return Response({'Status': '0', 'message': 'Product ID and quantity are required'}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user

        # Debugging print statement
        print(f"User ID: {user.id}")

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'Status': '0', 'message': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        # Debugging print statement
        print(f"Product ID: {product.id}, Stock: {product.stock}")

        if product.stock < int(quantity):
            return Response({'Status': '0', 'message': 'Insufficient stock'}, status=status.HTTP_400_BAD_REQUEST)

        cart, created = Cart.objects.get_or_create(user=user)
        # Debugging print statement
        print(f"Cart ID: {cart.id}, Created: {created}")

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        # Debugging print statement
        print(f"Cart Item: {cart_item}, Created: {created}")

        if created:
            cart_item.quantity = int(quantity)
        else:
            if cart_item.quantity + int(quantity) > product.stock:
                return Response({'Status': '0', 'message': 'Insufficient stock'}, status=status.HTTP_400_BAD_REQUEST)
            cart_item.quantity += int(quantity)

        cart_item.save()

        # Update the product stock
        product.stock -= int(quantity)
        if product.stock < 0:
            return Response({'Status': '0', 'message': 'Insufficient stock'}, status=status.HTTP_400_BAD_REQUEST)
        product.save()

        return Response({"Status": "1", "message": "Product added to cart successfully"}, status=status.HTTP_201_CREATED)
    
class GetCart(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            return Response({'Status': '0', 'message': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)

        cart_items = CartItem.objects.filter(cart=cart)

        # Prepare the cart items data
        items = []
        for item in cart_items:
            items.append({
                'product_id': item.product.id,
                'product_name': item.product.name,
                'quantity': item.quantity,
                'price_per_item': item.product.price,
                'total_price': item.quantity * item.product.price
            })

        return Response({
            'Status': '1',
            'cart_id': cart.id,
            'total_items': len(items),
            'items': items,
        }, status=status.HTTP_200_OK)    

class UpdateCart(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        product_id = request.data.get('productid')
        quantity = request.data.get('quantity')

        if not product_id or not quantity:
            return Response({'Status': '0', 'message': 'Product ID and quantity are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            quantity = int(quantity)
            if quantity <= 0:
                return Response({'Status': '0', 'message': 'Quantity must be a positive integer'}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({'Status': '0', 'message': 'Quantity must be a valid integer'}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'Status': '0', 'message': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            cart_item = CartItem.objects.get(cart__user=user, product=product)
        except CartItem.DoesNotExist:
            return Response({'Status': '0', 'message': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the stock is sufficient
        if product.stock >= quantity:
            # Calculate the change in quantity
            quantity_difference = quantity - cart_item.quantity

            # Update the cart item quantity
            cart_item.quantity = quantity
            cart_item.save()

            # Adjust the product stock
            product.stock -= quantity_difference
            product.save()

            return Response({'Status': '1', 'message': 'Cart item updated successfully'}, status=status.HTTP_200_OK)
        else:
            # Insufficient stock case
            return Response({'Status': '0', 'message': 'Insufficient stock'}, status=status.HTTP_400_BAD_REQUEST)
    

    # def post(self, request):
    #     product_id = request.data.get('productid')
    #     quantity = request.data.get('quantity')

    #     # if not product_id or not quantity:
    #     #     return Response({'Status': '0', 'message': 'Product ID and quantity are required'}, status=status.HTTP_400_BAD_REQUEST)

    #     # try:
    #     #     quantity = int(quantity)
    #     #     if quantity <= 0:
    #     #         return Response({'Status': '0', 'message': 'Quantity must be a positive integer'}, status=status.HTTP_400_BAD_REQUEST)
    #     # except ValueError:
    #     #     return Response({'Status': '0', 'message': 'Quantity must be a valid integer'}, status=status.HTTP_400_BAD_REQUEST)

    #     # user = request.user

    #     # try:
    #     #     cart = Cart.objects.get(user=user)
    #     # except Cart.DoesNotExist:
    #     #     return Response({'Status': '0', 'message': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)

    #     # try:
    #     #     cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
    #     # except CartItem.DoesNotExist:
    #     #     return Response({'Status': '0', 'message': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)

    #     # product = cart_item.product

    #     # if quantity > product.stock + cart_item.quantity:
    #     #     return Response({'Status': '0', 'message': 'Insufficient stock'}, status=status.HTTP_400_BAD_REQUEST)

    #     # # Calculate the change in quantity
    #     # quantity_difference = quantity - cart_item.quantity

    #     # # Update the cart item quantity
    #     # cart_item.quantity = quantity
    #     # cart_item.save()

    #     # # Adjust the product stock
    #     # product.stock -= quantity_difference
    #     # product.save()
    #     product = Product.objects.get(id=product_id)
    #     cart_item = CartItem.objects.get(product=product)
    #     print(cart_item.product)
    #     # try:
    #     if product.stock >= quantity:
    #             cart_item.quantity = quantity
    #             cart_item.save()
    #             return Response({'Status': '1', 'message': 'Cart item updated successfully'}, status=status.HTTP_200_OK)
    #     # except:
    #     else:
    #         print("noo----------------------------------------")
    #         return Response({'Status': '0', 'message': 'Insufficient stock'}, status=status.HTTP_400_BAD_REQUEST)
            # cart_item.quantity = quantity
            # cart_item.save()
            # return Response({'Status': '1', 'message': 'Cart item updated successfully'}, status=status.HTTP_200_OK)

   