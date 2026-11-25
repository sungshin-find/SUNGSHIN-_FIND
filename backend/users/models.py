from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
import random
from datetime import timedelta
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, email=None, password=None, username=None, **extra_fields):
        if not email and username:
            email = f'{username}@sungshin.ac.kr'
        if not email:
            raise ValueError('이메일은 필수 입력 항목입니다.')

        email = self.normalize_email(email)

        if 'nickname' not in extra_fields or not extra_fields['nickname']:
            extra_fields['nickname'] = username or email.split('@')[0]

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    nickname = models.CharField(max_length=30, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nickname']

    def __str__(self):
        return self.nickname

    def get_username(self):
        return self.nickname

    @property
    def username(self):
        return self.nickname

class EmailVerification(models.Model):
    email = models.EmailField(unique=True)
    code = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def create_or_update_code(cls, email, expire_minutes=5):
        code = f'{random.randint(0, 999999):06d}'
        expires_at = timezone.now() + timedelta(minutes=expire_minutes)
        obj, _ = cls.objects.update_or_create(
            email=email,
            defaults={
                'code': code,
                'is_verified': False,
                'expires_at': expires_at,
            },
        )
        return obj

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f'{self.email} ({self.code})'