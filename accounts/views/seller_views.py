from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied

from accounts.serializers import *
from accounts.models import *


from products.serializers import BrandSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import generics







        




class SellerSignupView(APIView):
    def post(self, request):
        serializer = SellerSignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Seller account created successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class CompanyDetailsView(generics.UpdateAPIView):
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_object(self):
        # Ensure the user is a seller and return the company object
        user = self.request.user
        if user.profile.user_type != 'seller':
            raise PermissionDenied("You are not authorized to access this resource.")
        return get_object_or_404(Company, vendor=user)

    def get(self, request, *args, **kwargs):
        # Return the company details of the logged-in user
        company = self.get_object()
        serializer = self.serializer_class(company)
        return Response(
            {"Status": "1", "message": "Success", "Data": serializer.data},
            status=status.HTTP_200_OK
        )

    def patch(self, request, *args, **kwargs):
        # Update the company details of the logged-in user
        company = self.get_object()
        serializer = self.serializer_class(company, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"Status": "1", "message": "Company details updated successfully.", "Data": serializer.data},
                status=status.HTTP_200_OK
            )
        return Response(
            {"Status": "0", "message": "Error updating company details.", "Errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )




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
    



# class BannerCreateView(APIView):
#     def get(self, request, format=None):
#         print("check")
#         banners = Banner.objects.all()
#         serializer = BannerSerializer(banners, many=True)
#         return Response({
#             "Status": "1",
#             "message": "Success",
#             "Data": serializer.data
#         })        
        
#     def post(self, request, format=None):
#         serializer = BannerSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({
#                 "Status": "1",
#                 "message": "Banner added successfully",
#                 "Data": serializer.data
#             }, status=status.HTTP_201_CREATED)
#         return Response({
#             "Status": "0",
#             "message": "Error",
#             "Errors": serializer.errors
#         }, status=status.HTTP_400_BAD_REQUEST)




