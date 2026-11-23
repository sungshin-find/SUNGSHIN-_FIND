from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'nickname', 'password', 'password_confirm', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_password(self, value):
        # Django 기본 비밀번호 정책(길이, 숫자 전용 방지, 유사도 등) 검증
        validate_password(value)
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password_confirm': '비밀번호가 일치하지 않습니다.'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        # create_user 내부에서 set_password()를 호출해 비밀번호를 해싱하여 저장
        user = User.objects.create_user(
            email=validated_data['email'],
            nickname=validated_data['nickname'],
            password=validated_data['password'],
        )
        return user