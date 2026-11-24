from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from .models import EmailVerification

User = get_user_model()
ALLOWED_EMAIL_DOMAIN = '@sungshin.ac.kr'

def validate_sungshin_email(email):
    normalized = email.strip().lower()
    if not normalized.endswith(ALLOWED_EMAIL_DOMAIN):
        raise serializers.ValidationError('성신여자대학교 이메일(@sungshin.ac.kr)만 사용할 수 있습니다.')
    return normalized

class EmailSendSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        email = validate_sungshin_email(value)
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError('이미 가입된 이메일입니다.')
        return email


class EmailVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6, min_length=6)

    def validate(self, attrs):
        email = validate_sungshin_email(attrs['email'])
        code = attrs['code'].strip()

        try:
            verification = EmailVerification.objects.get(email=email)
        except EmailVerification.DoesNotExist:
            raise serializers.ValidationError({'email': '인증 코드 발송 내역이 없습니다. 먼저 인증 코드를 요청해 주세요.'})

        if verification.is_expired():
            raise serializers.ValidationError({'code': '인증 코드가 만료되었습니다. 다시 요청해 주세요.'})

        if verification.code != code:
            raise serializers.ValidationError({'code': '인증 코드가 일치하지 않습니다.'})

        attrs['email'] = email
        attrs['verification'] = verification
        return attrs

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'nickname', 'password', 'password_confirm', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_email(self, value):
        email = validate_sungshin_email(value)
        if not EmailVerification.objects.filter(email=email, is_verified=True).exists():
            raise serializers.ValidationError('이메일 인증이 완료되지 않았습니다.')
        return email
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password_confirm': '비밀번호가 일치하지 않습니다.'})

        # 사용자 정보(email, nickname)와 비밀번호 간 유사도 검증을 위해 임시 User 객체 전달
        user = User(email=attrs.get('email', ''), nickname=attrs.get('nickname', ''))
        try:
            validate_password(attrs['password'], user=user)
        except DjangoValidationError as e:
            raise serializers.ValidationError({'password': list(e.messages)})

        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        # create_user 내부에서 set_password()를 호출해 비밀번호를 해싱하여 저장
        user = User.objects.create_user(
            email=validated_data['email'],
            nickname=validated_data['nickname'],
            password=validated_data['password'],
        )
        EmailVerification.objects.filter(email=user.email).delete()
        return user