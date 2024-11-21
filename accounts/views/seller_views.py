from accounts.serializers import SellerSignupSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from products.models import Banner

from products.serializers import BannerSerializer, BrandSerializer
from rest_framework.parsers import MultiPartParser, FormParser






        




class SellerSignupView(APIView):
    def post(self, request):
        serializer = SellerSignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Seller account created successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





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
