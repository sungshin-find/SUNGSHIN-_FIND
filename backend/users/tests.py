from django.test import TestCase
from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse
from django.utils import timezone

from .models import EmailVerification

User = get_user_model()


@pytest.mark.django_db
def test_send_verification_code_success():
    url = reverse('user-email-send')
    response = client_post_json(url, {'email': 'student@sungshin.ac.kr'})

    assert response.status_code == 200
    assert EmailVerification.objects.filter(email='student@sungshin.ac.kr', is_verified=False).exists()
    assert len(mail.outbox) == 1
    assert 'student@sungshin.ac.kr' in mail.outbox[0].to


@pytest.mark.django_db
def test_send_verification_code_invalid_domain():
    url = reverse('user-email-send')
    response = client_post_json(url, {'email': 'outsider@gmail.com'})

    assert response.status_code == 400
    assert 'email' in response.json()
    assert len(mail.outbox) == 0


@pytest.mark.django_db
def test_verify_code_success():
    verification = EmailVerification.create_or_update_code(email='student@sungshin.ac.kr')
    url = reverse('user-email-verify')
    response = client_post_json(url, {'email': 'student@sungshin.ac.kr', 'code': verification.code})

    assert response.status_code == 200
    verification.refresh_from_db()
    assert verification.is_verified is True


@pytest.mark.django_db
def test_verify_code_wrong_code():
    verification = EmailVerification.create_or_update_code(email='student@sungshin.ac.kr')
    wrong_code = '000000' if verification.code != '000000' else '999999'

    url = reverse('user-email-verify')
    response = client_post_json(url, {'email': 'student@sungshin.ac.kr', 'code': wrong_code})

    assert response.status_code == 400
    assert 'code' in response.json()


@pytest.mark.django_db
def test_verify_code_expired():
    verification = EmailVerification.create_or_update_code(email='student@sungshin.ac.kr')
    # 만료 시간을 과거(1분 전)로 강제 설정하여 만료 상황 재현
    verification.expires_at = timezone.now() - timedelta(minutes=1)
    verification.save(update_fields=['expires_at'])

    url = reverse('user-email-verify')
    response = client_post_json(url, {'email': 'student@sungshin.ac.kr', 'code': verification.code})

    assert response.status_code == 400
    assert 'code' in response.json()


@pytest.mark.django_db
def test_signup_requires_verified_email():
    url = reverse('user-signup')
    payload = {
        'email': 'unverified@sungshin.ac.kr',
        'nickname': '미인증수룡',
        'password': 'StrongPassword123!',
        'password_confirm': 'StrongPassword123!',
    }
    response = client_post_json(url, payload)

    assert response.status_code == 400
    assert 'email' in response.json()


@pytest.mark.django_db
def test_signup_success():
    email = 'test@sungshin.ac.kr'
    EmailVerification.objects.create(
        email=email,
        code='123456',
        is_verified=True,
        expires_at=timezone.now() + timedelta(minutes=5),
    )

    url = reverse('user-signup')
    payload = {
        'email': email,
        'nickname': '수룡이',
        'password': 'StrongPassword123!',
        'password_confirm': 'StrongPassword123!',
    }
    response = client_post_json(url, payload)

    assert response.status_code == 201
    data = response.json()
    assert data['email'] == email
    assert data['nickname'] == '수룡이'
    assert 'password' not in data

    user = User.objects.get(email=email)
    assert user.check_password('StrongPassword123!')
    # 가입 완료 후 인증 레코드가 정리되었는지 확인
    assert not EmailVerification.objects.filter(email=email).exists()


@pytest.mark.django_db
def test_signup_password_mismatch():
    email = 'mismatch@sungshin.ac.kr'
    EmailVerification.objects.create(
        email=email,
        code='123456',
        is_verified=True,
        expires_at=timezone.now() + timedelta(minutes=5),
    )

    url = reverse('user-signup')
    payload = {
        'email': email,
        'nickname': '수룡이2',
        'password': 'StrongPassword123!',
        'password_confirm': 'DifferentPassword123!',
    }
    response = client_post_json(url, payload)

    assert response.status_code == 400
    assert 'password_confirm' in response.json()


@pytest.mark.django_db
def test_signup_weak_password():
    email = 'weak@sungshin.ac.kr'
    EmailVerification.objects.create(
        email=email,
        code='123456',
        is_verified=True,
        expires_at=timezone.now() + timedelta(minutes=5),
    )

    url = reverse('user-signup')
    payload = {
        'email': email,
        'nickname': '수룡이3',
        'password': '123',
        'password_confirm': '123',
    }
    response = client_post_json(url, payload)

    assert response.status_code == 400
    assert 'password' in response.json()


@pytest.mark.django_db
def test_signup_duplicate_email():
    User.objects.create_user(
        email='dup@sungshin.ac.kr',
        nickname='기존수룡',
        password='StrongPassword123!',
    )
    url = reverse('user-signup')
    payload = {
        'email': 'dup@sungshin.ac.kr',
        'nickname': '새수룡',
        'password': 'StrongPassword123!',
        'password_confirm': 'StrongPassword123!',
    }
    response = client_post_json(url, payload)

    assert response.status_code == 400
    assert 'email' in response.json()


@pytest.mark.django_db
def test_signup_duplicate_nickname():
    User.objects.create_user(
        email='existing@sungshin.ac.kr',
        nickname='중복닉네임',
        password='StrongPassword123!',
    )
    EmailVerification.objects.create(
        email='new@sungshin.ac.kr',
        code='123456',
        is_verified=True,
        expires_at=timezone.now() + timedelta(minutes=5),
    )

    url = reverse('user-signup')
    payload = {
        'email': 'new@sungshin.ac.kr',
        'nickname': '중복닉네임',
        'password': 'StrongPassword123!',
        'password_confirm': 'StrongPassword123!',
    }
    response = client_post_json(url, payload)

    assert response.status_code == 400
    assert 'nickname' in response.json()


def client_post_json(url, payload):
    from django.test import Client

    return Client().post(url, data=payload, content_type='application/json')