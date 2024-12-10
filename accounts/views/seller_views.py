from accounts.serializers import *
from accounts.models import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from products.models import Banner

from products.serializers import BannerSerializer, BrandSerializer
from rest_framework.parsers import MultiPartParser, FormParser

from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication


from rest_framework import generics

from django.core.exceptions import PermissionDenied
from django.db.models import Avg



        




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
    



class BannerCreateView(APIView):
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




class AppFeedbackListView(generics.ListAPIView):
    serializer_class = AppFeedbackSerializer
    queryset = AppFeedback.objects.all()
    # permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        # Get queryset
        queryset = self.filter_queryset(self.get_queryset())

        # Serialize the data
        serializer = self.get_serializer(queryset, many=True)

        # Custom response format
        return Response(
            {
                "Status": "1",
                "message": "Success",
                "Data": serializer.data
            },
            status=status.HTTP_200_OK
        )
    
def get_overall_app_rating():
    # Calculate the average rating of all reviews in the system
    average_rating = AppFeedback.objects.aggregate(Avg('rating'))['rating__avg']
    return average_rating or 0  # Return 0 if no reviews exist



class OverallFeedbackView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Get the overall rating using the utility function
        overall_rating = get_overall_app_rating()

        return Response({
            "Status": "1",
            "message": "Success",
            "Overall App Rating": overall_rating
        }, status=status.HTTP_200_OK)