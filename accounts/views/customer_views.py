from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import get_object_or_404


import json
from PIL import Image


from accounts.models import *
from accounts.serializers import *
from orders.models import Cart, CartItem
from products.models import Wishlist, WishlistItem


from rest_framework.exceptions import ValidationError
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListCreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import generics
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token




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



# class BannerListView(APIView):
#     def get(self, request, format=None):
#         print("check")
#         banners = Banner.objects.all()
#         serializer = BannerSerializer(banners, many=True)
#         return Response({
#             "Status": "1",
#             "message": "Success",
#             "Data": serializer.data
#         })  
        




class ProfileListCreateView(generics.ListCreateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
#below code added ---------------------
    def perform_create(self, serializer):
        user = self.request.user
        if user and not Profile.objects.filter(user=user).exists():
            serializer.save(user=user)
        else:
            serializer.save()




class ProfileRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer  




class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError:
            return Response({
                "status": "0",
                "message": "Invalid username or password"
            }, status=status.HTTP_400_BAD_REQUEST)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        user_type = token.user.profile.user_type
        print(user_type)
        data = {"access": token.key, "user_type": user_type, "user_name": user.username, "email": user.email}
        if user_type == "customer":
            self.merge_cart(user)
            self.merge_wishlist(user)
            try:
                cart = Cart.objects.get(user=user)
                cart_items = CartItem.objects.filter(cart=cart).count()
            except:
                cart_items = 0
            data = {"access": token.key, "user_type": user_type, "user_name": user.username, "email": user.email, "total_items": cart_items}
            return Response({
                "status": "1",
                "message": "Success",
                "Data": data
            })
        else:
            return Response({
                "status": "1",
                "message": "Success",
                "Data": data
            })
        
    def merge_cart(self, user):
        session_id = self.request.headers.get('Session-Id', None)
        if not session_id:
            session_id = self.request.session.session_key
        anonymous_cart = Cart.objects.filter(session_id=session_id, user=None).first()

        if anonymous_cart:
            user_cart, _ = Cart.objects.get_or_create(user=user)

            # Move items from the anonymous cart to the user's cart
            for item in CartItem.objects.filter(cart=anonymous_cart):
                cart_item, cart_created = CartItem.objects.get_or_create(cart=user_cart, product=item.product)
                # cart_item.quantity += item.quantity
                cart_item.quantity = item.quantity if cart_created else cart_item.quantity + item.quantity
                cart_item.save()

            anonymous_cart.delete()

    def merge_wishlist(self, user):
        session_id = self.request.headers.get('Session-Id', None)
        if not session_id:
            session_id = self.request.session.session_key
        anonymous_wishlist = Wishlist.objects.filter(session_id=session_id, user=None).first()

        if anonymous_wishlist:
            user_wishlist, _ = Wishlist.objects.get_or_create(user=user)

            # Move items from the anonymous cart to the user's cart
            for item in WishlistItem.objects.filter(wishlist=anonymous_wishlist):
                wishlist_item, wishlist_created = WishlistItem.objects.get_or_create(wishlist=user_wishlist, product=item.product)
                # cart_item.quantity += item.quantity
                # cart_item.quantity = item.quantity if cart_created else cart_item.quantity + item.quantity
                # cart_item.save()

            anonymous_wishlist.delete()

class LogoutView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Delete the token associated with the current user
        Token.objects.filter(user=request.user).delete()
        return Response({"detail": "Successfully logged out."})
    


class ProfileUpdateView(generics.UpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_object(self):
        # Fetch the profile of the currently logged-in user
        return get_object_or_404(Profile, user=self.request.user)

    def get(self, request, *args, **kwargs):
        # This method will return the profile of the currently logged-in user
        profile = self.get_object()
        serializer = ProfileSerializer(profile)
        return Response({"Status": "1", "message": "Success", "Data": [serializer.data]}, status=status.HTTP_200_OK)


    def patch(self, request, *args, **kwargs):
        profile = self.get_object()
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({"Status": "1", "message": "Success", "Data": [serializer.data]})

    def perform_update(self, serializer):
        # Custom logic (if needed) before saving
        serializer.save()


class CustomerSignupView(APIView):
    def post(self, request):
        email = request.data["email"]
        try:
            tempuser = TemporaryUserContact.objects.get(email=email)
            if tempuser:
                tempuser.delete()
        except:
            pass
        serializer = CustomerSignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User created successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


    




class DeliveryAddressListCreateView(ListCreateAPIView):
    serializer_class = DeliveryAddressSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]


    def get_queryset(self):
        # Get only the delivery addresses of the authenticated user
        user = self.request.user
        profile = Profile.objects.get(user=user)
        
        # Get the default address and remaining addresses
        default_address = profile.default_address
        addresses = DeliveryAddress.objects.filter(user=user).exclude(id=default_address.id if default_address else None)
        print(addresses)
        if default_address:
            return DeliveryAddress.objects.filter(id=default_address.id).union(addresses)
        else:
            return addresses

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({"Status": "1", "message": "Success", "data": serializer.data}, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            delivery_address = serializer.save(user=self.request.user)
            profile = Profile.objects.get(user=self.request.user)
            if profile.default_address is None:
                # If no default address, set this new address as the default
                profile.default_address = delivery_address
                profile.save()
            # self.perform_create(serializer)
            return Response({"Status": "1", "message": "Address added successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"Status": "0", "message": "Failed to add address", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)





class DeliveryAddressDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = DeliveryAddressSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        # Ensure that users can only interact with their own addresses
        return DeliveryAddress.objects.filter(user=self.request.user)

    def get_object(self):
        # Retrieve the address and check if it belongs to the current user
        obj = super().get_object()
        if obj.user != self.request.user:
            raise PermissionDenied("You do not have permission to access this address.")
        return obj

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({"Status": "1", "message": "Success", "data": serializer.data}, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response({"Status": "1", "message": "Address updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"Status": "0", "message": "Failed to update address", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"Status": "1", "message": "Address deleted successfully"}, status=status.HTTP_200_OK)

    def perform_destroy(self, instance):
        instance.delete()




class DefaultDeliveryAddressView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    # GET method to retrieve the default address
    def get(self, request):
        user = request.user
        try:
            profile = Profile.objects.get(user=user)
            try:
                default_address = profile.default_address
            except:
                return Response({"Status": "0", "message": "No default address found"}, status=status.HTTP_404_NOT_FOUND)
            
            # default_address = DeliveryAddress.objects.get(user=user, is_default=True)
            if default_address != None:
                delivery_address_serializer = DeliveryAddressSerializer(default_address)
                return Response({"Status": "1", "message": "Success", "data": [delivery_address_serializer.data]}, status=status.HTTP_200_OK)
            else:
                return Response({"Status": "0", "message": "No default address found"}, status=status.HTTP_404_NOT_FOUND)
        except DeliveryAddress.DoesNotExist:
            return Response({"Status": "0", "message": "No user found"}, status=status.HTTP_404_NOT_FOUND)

    # POST method to set a new default address
    def post(self, request):
        user = request.user
        new_default_address_id = request.data.get('default_address')  # Get the ID of the new default address

        try:
            new_default_address = DeliveryAddress.objects.get(id=new_default_address_id, user=user)  # Fetch the new default address
        except DeliveryAddress.DoesNotExist:
            return Response({"Status": "0", "message": "Address not found"}, status=status.HTTP_404_NOT_FOUND)

        profile = Profile.objects.get(user=user)
        profile.default_address = new_default_address
        profile.save()
        delivery_address_serializer = DeliveryAddressSerializer(new_default_address)
        return Response({"Status": "1", "message": "Default address updated successfully", "data": delivery_address_serializer.data}, status=status.HTTP_200_OK)

    



class SuperAdminContactView(APIView):
    def get(self, request):
        contacts = SuperAdmin.objects.all()
        contact_list = []

        for contact in contacts:
            contact_list.append({
                'purpose': contact.purpose,
                'phone_number': contact.phone_number,
                'content': 'This is a sample content.'
            })

        return Response({
            'Status': '1',
            'message': 'Success',
            'Data': contact_list
        }, status=status.HTTP_200_OK)
    




class SimpleProfileView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        user = request.user if request.user.is_authenticated else None
        if not request.session.session_key:
            print("No session id")
            request.session['initialized'] = True  # Initialize the session
            request.session.save()
        session_id = request.session.session_key
        print(session_id)
        if user:
            profile = Profile.objects.get(user=user)
            data = {
                "username": user.username,
                "mobile": profile.mobile_number if profile.mobile_number else ""
            }
        else:
            # temp_details = TemporaryUserContact.objects.get(session_id=session_id)
            temp_details = get_object_or_404(TemporaryUserContact, session_id=session_id)
            
            data = {
                "email": temp_details.email,
                "mobile": temp_details.mobile_number
            }
        
        return Response({
            'Status': '1',
            'message': 'Success',
            'data': [data]
        })
    


class TemporaryUserCreateView(APIView):
    def post(self, request):
        email = request.data.get('email')
        mobile = request.data.get('mobile_number')

        if not request.session.session_key:
            request.session['initialized'] = True  # Initialize the session
            request.session.save()
        session_id = request.session.session_key

        # Basic validation to ensure email and mobile are provided
        if not email or not mobile:
            return Response({
                'Status': '1',
                'message': 'Email and mobile number are required.'
            }, status=status.HTTP_200_OK)

        # Check if email or mobile already exists in TemporaryUserContact
        if TemporaryUserContact.objects.filter(email=email).exists():
            return Response({
                'Status': '1',
                'message': 'Success'
            }, status=status.HTTP_200_OK)

        if TemporaryUserContact.objects.filter(mobile_number=mobile).exists():
            return Response({
                'Status': '1',
                'message': 'Success'
            }, status=status.HTTP_200_OK)

        try:
            # Create the temporary user contact
            TemporaryUserContact.objects.create(email=email, mobile_number=mobile, session_id=session_id)
        except ValidationError as e:
            return Response({
                'Status': '0',
                'message': f'Validation error: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'Status': '1',
            'message': 'Success'
        }, status=status.HTTP_201_CREATED)
    


class WebCreateSessionIdView(APIView):
    def get(self, request):
        session_id = request.headers.get('Session-Id', None)
        if not session_id:
            if not request.session.session_key:
                request.session.create()
            session_id = request.session.session_key
        try:
            cart = Cart.objects.get(session_id=session_id)
            cart_items = CartItem.objects.filter(cart=cart).count()
        except Cart.DoesNotExist:
            cart_items = 0

        # Return session ID and cart item count in the response
        return JsonResponse({
            'Status': '1',
            'message': 'Success',
            'sessionid': session_id,  # Send session ID in the response body
            'Data': cart_items,
        })


class CreateSessionIdView(APIView):
    def get(self, request):
        # Create a session if it doesn't exist
        user = request.user if request.user.is_authenticated else None
        session_id = request.headers.get('Session-Id', None)
        if not session_id:
            if not request.session.session_key:
                request.session.create()
            session_id = request.session.session_key
        
        try:
            cart = Cart.objects.get(user=user) if user else Cart.objects.get(session_id=session_id)
            # cart = Cart.objects.get(session_id=session_id)
            cart_items = CartItem.objects.filter(cart=cart).count()
        except Cart.DoesNotExist:
            cart_items = 0

        # Prepare the response
        return Response({
            'Status': '1',
            'message': 'Success',
            'Data': cart_items,
            'sessionid': session_id
        }, status=status.HTTP_200_OK)