import datetime

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from .models import Post


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user():
    return get_user_model().objects.create_user(username='yuri', password='pass1234!')


@pytest.fixture
def other_user():
    return get_user_model().objects.create_user(username='naeun', password='pass1234!')


def make_payload(**overrides):
    payload = {
        'post_type': 'LOST',
        'title': '검정 카드지갑 잃어버렸어요',
        'category': 'WALLET',
        'color': 'BLACK',
        'location': 'SUNGSHIN',
        'location_detail': '3층 강의실',
        'event_date': str(timezone.localdate()),
        'description': '학생증이 들어 있어요',
    }
    payload.update(overrides)
    return payload


def make_post(author, **overrides):
    data = make_payload(**overrides)
    data['event_date'] = datetime.date.fromisoformat(data['event_date'])
    return Post.objects.create(author=author, **data)


@pytest.mark.django_db
def test_create_post_sets_author(api_client, user):
    api_client.force_authenticate(user)
    response = api_client.post(reverse('post-list'), make_payload(), format='json')

    assert response.status_code == 201
    assert response.data['author'] == 'yuri'
    assert response.data['status'] == 'OPEN'
    assert response.data['category_display'] == '지갑'
    assert Post.objects.get().author == user


@pytest.mark.django_db
def test_create_post_requires_login(api_client):
    response = api_client.post(reverse('post-list'), make_payload(), format='json')
    assert response.status_code in (401, 403)
    assert Post.objects.count() == 0


@pytest.mark.django_db
def test_invalid_choice_rejected(api_client, user):
    api_client.force_authenticate(user)
    response = api_client.post(reverse('post-list'), make_payload(category='SPACESHIP'), format='json')
    assert response.status_code == 400
    assert 'category' in response.data


@pytest.mark.django_db
def test_future_event_date_rejected(api_client, user):
    api_client.force_authenticate(user)
    tomorrow = timezone.localdate() + datetime.timedelta(days=1)
    response = api_client.post(reverse('post-list'), make_payload(event_date=str(tomorrow)), format='json')
    assert response.status_code == 400
    assert 'event_date' in response.data


@pytest.mark.django_db
def test_list_filter_by_type(api_client, user):
    make_post(user, post_type='LOST')
    make_post(user, post_type='FOUND')

    response = api_client.get(reverse('post-list'), {'type': 'FOUND'})

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]['post_type'] == 'FOUND'


@pytest.mark.django_db
def test_only_author_can_update(api_client, user, other_user):
    post = make_post(user)
    url = reverse('post-detail', args=[post.id])

    api_client.force_authenticate(other_user)
    assert api_client.patch(url, {'title': '남이 수정'}, format='json').status_code == 403

    api_client.force_authenticate(user)
    response = api_client.patch(url, {'title': '수정된 제목'}, format='json')
    assert response.status_code == 200
    assert response.data['title'] == '수정된 제목'


@pytest.mark.django_db
def test_only_author_can_delete(api_client, user, other_user):
    post = make_post(user)
    url = reverse('post-detail', args=[post.id])

    api_client.force_authenticate(other_user)
    assert api_client.delete(url).status_code == 403

    api_client.force_authenticate(user)
    assert api_client.delete(url).status_code == 204
    assert Post.objects.count() == 0


@pytest.mark.django_db
def test_status_cannot_be_changed_by_create(api_client, user):
    api_client.force_authenticate(user)
    response = api_client.post(reverse('post-list'), make_payload(status='RETURNED'), format='json')
    assert response.status_code == 201
    assert response.data['status'] == 'OPEN'


def test_choices_endpoint(api_client):
    response = api_client.get(reverse('post-choices'))
    assert response.status_code == 200
    assert {'value': 'WALLET', 'label': '지갑'} in response.data['category']
    assert {'value': 'SUNGSHIN', 'label': '성신관'} in response.data['location']
