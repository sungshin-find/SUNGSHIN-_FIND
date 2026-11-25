from django.test import TestCase
from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse
from django.utils import timezone
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

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

@pytest.mark.django_db
def test_jwt_login_and_refresh_success():
    User.objects.create_user(
        email='jwtuser@sungshin.ac.kr',
        nickname='토큰수룡',
        password='StrongPassword123!',
    )
    from django.test import Client

    client = Client()

    # 1. 로그인 (access, refresh 토큰 발급 확인)
    login_url = reverse('user-login')
    login_res = client.post(
        login_url,
        data={'email': 'jwtuser@sungshin.ac.kr', 'password': 'StrongPassword123!'},
        content_type='application/json',
    )
    assert login_res.status_code == 200
    tokens = login_res.json()
    assert 'access' in tokens
    assert 'refresh' in tokens

    # 2. 토큰 갱신 (새 access 토큰 발급 확인)
    refresh_url = reverse('user-token-refresh')
    refresh_res = client.post(
        refresh_url,
        data={'refresh': tokens['refresh']},
        content_type='application/json',
    )
    assert refresh_res.status_code == 200
    assert 'access' in refresh_res.json()


@pytest.mark.django_db
def test_jwt_login_invalid_credentials():
    User.objects.create_user(
        email='jwtuser2@sungshin.ac.kr',
        nickname='토큰수룡2',
        password='StrongPassword123!',
    )
    response = client_post_json(
        reverse('user-login'),
        {'email': 'jwtuser2@sungshin.ac.kr', 'password': 'WrongPassword!'},
    )
    assert response.status_code == 401


@pytest.mark.django_db
def test_post_create_requires_jwt_authentication():
    from django.test import Client

    client = Client()
    posts_url = '/api/posts/'
    post_payload = {
        'post_type': 'LOST',
        'title': '지갑 분실했습니다',
        'content': '성신관 3층에서 잃어버렸어요',
        'category': 'WALLET',
        'color': 'BLACK',
        'location': 'SUNGSHIN',
        'event_date': '2026-11-25',
    }

    # 1. 비로그인(토큰 없음) 상태 게시물 작성 -> 401 또는 403 차단 확인
    unauth_res = client.post(posts_url, data=post_payload, content_type='application/json')
    assert unauth_res.status_code in (401, 403)

    # 2. 로그인 후 Bearer 토큰 포함하여 게시물 작성 -> 201 성공 확인
    User.objects.create_user(
        email='poster@sungshin.ac.kr',
        nickname='작성자수룡',
        password='StrongPassword123!',
    )
    login_res = client.post(
        reverse('user-login'),
        data={'email': 'poster@sungshin.ac.kr', 'password': 'StrongPassword123!'},
        content_type='application/json',
    )
    access_token = login_res.json()['access']

    auth_res = client.post(
        posts_url,
        data=post_payload,
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {access_token}',
    )
    assert auth_res.status_code == 201