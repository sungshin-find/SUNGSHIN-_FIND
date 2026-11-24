from django.test import TestCase

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


@pytest.mark.django_db
def test_signup_success(client):
    url = reverse('user-signup')
    payload = {
        'email': 'test@sungshin.ac.kr',
        'nickname': '수룡이',
        'password': 'StrongPassword123!',
        'password_confirm': 'StrongPassword123!',
    }
    response = client.post(url, data=payload, content_type='application/json')

    assert response.status_code == 201
    data = response.json()
    assert data['email'] == 'test@sungshin.ac.kr'
    assert data['nickname'] == '수룡이'
    assert 'password' not in data  # 응답에 비밀번호가 노출되지 않는지 확인

    # DB 저장 및 비밀번호 해싱 검증
    user = User.objects.get(email='test@sungshin.ac.kr')
    assert user.password != 'StrongPassword123!'
    assert user.check_password('StrongPassword123!')


@pytest.mark.django_db
def test_signup_password_mismatch(client):
    url = reverse('user-signup')
    payload = {
        'email': 'mismatch@sungshin.ac.kr',
        'nickname': '수룡이2',
        'password': 'StrongPassword123!',
        'password_confirm': 'DifferentPassword123!',
    }
    response = client.post(url, data=payload, content_type='application/json')

    assert response.status_code == 400
    assert 'password_confirm' in response.json()


@pytest.mark.django_db
def test_signup_weak_password(client):
    url = reverse('user-signup')
    payload = {
        'email': 'weak@sungshin.ac.kr',
        'nickname': '수룡이3',
        'password': '123',
        'password_confirm': '123',
    }
    response = client.post(url, data=payload, content_type='application/json')

    assert response.status_code == 400
    assert 'password' in response.json()


@pytest.mark.django_db
def test_signup_duplicate_email(client):
    User.objects.create_user(
        email='dup@sungshin.ac.kr',
        nickname='기존유저',
        password='StrongPassword123!',
    )
    url = reverse('user-signup')
    payload = {
        'email': 'dup@sungshin.ac.kr',
        'nickname': '새유저',
        'password': 'StrongPassword123!',
        'password_confirm': 'StrongPassword123!',
    }
    response = client.post(url, data=payload, content_type='application/json')

    assert response.status_code == 400
    assert 'email' in response.json()

@pytest.mark.django_db
def test_signup_duplicate_nickname(client):
    User.objects.create_user(
        email='existing@sungshin.ac.kr',
        nickname='중복닉네임',
        password='StrongPassword123!',
    )
    url = reverse('user-signup')
    payload = {
        'email': 'new@sungshin.ac.kr',
        'nickname': '중복닉네임',
        'password': 'StrongPassword123!',
        'password_confirm': 'StrongPassword123!',
    }
    response = client.post(url, data=payload, content_type='application/json')

    assert response.status_code == 400
    assert 'nickname' in response.json()