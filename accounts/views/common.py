from accounts.serializers import *
from accounts.models import *

from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

import random
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password





class AppReviewCreateView(generics.CreateAPIView):
    serializer_class = AppFeedbackSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Attach the currently authenticated user to the review
        serializer.save(user=self.request.user)

    def post(self, request, *args, **kwargs):
        # Create the review
        return self.create(request, *args, **kwargs)
    


class RequestPasswordResetView(APIView):
    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"Status": "0", "message": "User with this email does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        # Generate OTP
        otp = str(random.randint(100000, 999999))
        PasswordResetOTP.objects.create(user=user, otp=otp)

        # Send OTP via email
        send_mail(
            subject="Password Reset OTP",
            message=f"Your OTP for password reset is {otp}. It is valid for 10 minutes.",
            from_email="Pokaktech1@gmail.com",
            recipient_list=[email],
        )

        return Response({"Status": "1", "message": "OTP sent to your email"}, status=status.HTTP_200_OK)
    


class VerifyOTPView(APIView):
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"Status": "0", "message": "Invalid email"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            otp_record = PasswordResetOTP.objects.filter(user=user, otp=otp).latest('created_at')
        except PasswordResetOTP.DoesNotExist:
            return Response({"Status": "0", "message": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)

        if not otp_record.is_valid():
            return Response({"Status": "0", "message": "OTP has expired"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"Status": "1", "message": "OTP verified successfully"}, status=status.HTTP_200_OK)






class ResetPasswordView(APIView):
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        new_password = request.data.get('new_password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"Status": "0", "message": "Invalid email"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            otp_record = PasswordResetOTP.objects.filter(user=user, otp=otp).latest('created_at')
        except PasswordResetOTP.DoesNotExist:
            return Response({"Status": "0", "message": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)

        if not otp_record.is_valid():
            return Response({"Status": "0", "message": "OTP has expired"}, status=status.HTTP_400_BAD_REQUEST)

        # Reset password
        user.password = make_password(new_password)
        user.save()

        # Clean up used OTPs
        PasswordResetOTP.objects.filter(user=user).delete()

        return Response({"Status": "1", "message": "Password reset successfully"}, status=status.HTTP_200_OK)
