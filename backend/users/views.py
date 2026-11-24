from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import EmailVerification
from .serializers import EmailSendSerializer, EmailVerifySerializer, SignupSerializer

class EmailSendView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = EmailSendSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        verification = EmailVerification.create_or_update_code(email=email, expire_minutes=5)

        send_mail(
            subject='[성신파인드] 회원가입 이메일 인증 코드',
            message=f'인증 코드: {verification.code}\n5분 이내에 입력해 주세요.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        return Response({'message': '인증 코드가 발송되었습니다.'}, status=status.HTTP_200_OK)


class EmailVerifyView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = EmailVerifySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        verification = serializer.validated_data['verification']
        verification.is_verified = True
        verification.save(update_fields=['is_verified'])
        return Response({'message': '이메일 인증이 완료되었습니다.'}, status=status.HTTP_200_OK)

class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(SignupSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Create your views here.
