from accounts.serializers import *
from accounts.models import *

from rest_framework.permissions import IsAuthenticated
from rest_framework import generics








class AppReviewCreateView(generics.CreateAPIView):
    serializer_class = AppFeedbackSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Attach the currently authenticated user to the review
        serializer.save(user=self.request.user)

    def post(self, request, *args, **kwargs):
        # Create the review
        return self.create(request, *args, **kwargs)