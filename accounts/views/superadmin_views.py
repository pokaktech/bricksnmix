from django.db.models import Avg

from accounts.serializers import *
from accounts.models import *

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics





# def get_overall_app_rating_by_customer():
#     # Calculate the average rating of all reviews in the system
#     average_rating = AppFeedback.objects.filter(user__profile__user_type='customer').aggregate(Avg('rating'))['rating__avg']
#     return average_rating or 0  # Return 0 if no reviews exist





# def get_overall_app_rating_by_sellers():
#     # Filter reviews where the user is a seller and calculate the average rating
#     average_rating = AppFeedback.objects.filter(user__profile__user_type='seller').aggregate(Avg('rating'))['rating__avg']
#     return average_rating or 0  # Return 0 if no reviews exist


def get_overall_app_rating(user_type):
    # Filter reviews where the user is a seller and calculate the average rating
    average_rating = AppFeedback.objects.filter(user__profile__user_type=user_type).aggregate(Avg('rating'))['rating__avg']
    return average_rating or 0.0  # Return 0 if no reviews exist


# class CustomerFeedbackListView(generics.ListAPIView):
#     serializer_class = AppFeedbackSerializer
#     queryset = AppFeedback.objects.filter(user__profile__user_type="customer")
#     # permission_classes = [IsAuthenticated]

#     def list(self, request, *args, **kwargs):
#         # Get queryset
#         queryset = self.filter_queryset(self.get_queryset())

#         # Serialize the data
#         serializer = self.get_serializer(queryset, many=True)

#         # Custom response format
#         return Response(
#             {
#                 "Status": "1",
#                 "message": "Success",
#                 "Data": serializer.data
#             },
#             status=status.HTTP_200_OK
#         )
    




# class CustomerOverallFeedbackView(APIView):
#     # permission_classes = [IsAuthenticated]

#     def get(self, request, *args, **kwargs):
#         # Get the overall rating using the utility function
#         overall_rating = get_overall_app_rating_by_customer()

#         return Response({
#             "Status": "1",
#             "message": "Success",
#             "Overall Customer App Rating": overall_rating
#         }, status=status.HTTP_200_OK)
    





# class SellerFeedbackListView(generics.ListAPIView):
#     serializer_class = AppFeedbackSerializer
#     queryset = AppFeedback.objects.filter(user__profile__user_type="seller")
#     # permission_classes = [IsAuthenticated]

#     def list(self, request, *args, **kwargs):
#         # Get queryset
#         queryset = self.filter_queryset(self.get_queryset())

#         # Serialize the data
#         serializer = self.get_serializer(queryset, many=True)

#         # Custom response format
#         return Response(
#             {
#                 "Status": "1",
#                 "message": "Success",
#                 "Data": serializer.data
#             },
#             status=status.HTTP_200_OK
#         )
    




# class SellerOverallFeedbackView(APIView):
#     # permission_classes = [IsAuthenticated]

#     def get(self, request, *args, **kwargs):
#         # Get the overall rating using the utility function
#         overall_rating = get_overall_app_rating()

#         return Response({
#             "Status": "1",
#             "message": "Success",
#             "Overall Seller App Rating": overall_rating
#         }, status=status.HTTP_200_OK)
    





class FeedbackListView(APIView):

    def get(self, request, *args, **kwargs):
        user_type = request.query_params.get('user_type')
        
        if user_type == 'customer':
            feedbacks = AppFeedback.objects.filter(user__profile__user_type='customer')
        elif user_type == 'seller':
            feedbacks = AppFeedback.objects.filter(user__profile__user_type='seller')
        else:
            feedbacks = AppFeedback.objects.all()
        
        serializer = AppFeedbackSerializer(feedbacks, many=True)
        return Response({
            "status": '1',
            "message": "Success",
            "data": serializer.data
        }, status=200)




class OverallFeedbackView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user_type = request.query_params.get('user_type')
        # Get the overall rating using the utility function
        overall_rating = get_overall_app_rating(user_type=user_type)

        return Response({
            "Status": "1",
            "message": "Success",
            f"Overall {user_type} App Rating": overall_rating
        }, status=status.HTTP_200_OK)