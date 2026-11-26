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
def test_mine_filter(api_client, user, other_user):
    make_post(user)
    make_post(other_user)

    # 비로그인: "내 글"이 없으므로 빈 목록 (전체 목록이 나오면 안 됨)
    response = api_client.get(reverse('post-list'), {'mine': 'true'})
    assert response.status_code == 200
    assert response.data == []

    api_client.force_authenticate(user)
    response = api_client.get(reverse('post-list'), {'mine': 'true'})
    assert [p['author'] for p in response.data] == ['yuri']


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

@pytest.mark.django_db
def test_search_and_filters(api_client, user):
    today = timezone.localdate()
    yesterday = today - datetime.timedelta(days=1)

    p1 = make_post(
        user,
        title='검정 카드지갑 잃어버렸어요',
        category='WALLET',
        location='SUNGSHIN',
        location_detail='성신관 302호',
        description='학생증이 들어있어요',
        event_date=str(yesterday),
    )
    make_post(
        user,
        title='흰색 에어팟 주웠습니다',
        category='EARPHONE',
        location='SUJEONG',
        location_detail='수정관 로비',
        description='케이스만 있어요',
        event_date=str(today),
    )

    # 1. 키워드 검색 (제목 / 상세 설명 / 상세 장소)
    res_q = api_client.get(reverse('post-list'), {'q': '학생증'})
    assert res_q.status_code == 200
    assert [item['id'] for item in res_q.data] == [p1.id]

    # 2. 종류 + 장소 + 단일 날짜 복합 필터
    res_filter = api_client.get(
        reverse('post-list'),
        {
            'category': 'WALLET',
            'location': 'SUNGSHIN',
            'date': str(yesterday),
        },
    )
    assert res_filter.status_code == 200
    assert [item['id'] for item in res_filter.data] == [p1.id]

    # 3. 날짜 범위 필터 (date_from ~ date_to)
    res_range = api_client.get(
        reverse('post-list'),
        {'date_from': str(today), 'date_to': str(today)},
    )
    assert res_range.status_code == 200
    assert len(res_range.data) == 1
    assert res_range.data[0]['category'] == 'EARPHONE'


@pytest.mark.django_db
def test_status_change_and_match_exclusion(api_client, user, other_user):
    from .matching import update_matches
    from .models import Match

    lost_post = make_post(user, post_type='LOST', category='WALLET', color='BLACK', location='SUNGSHIN')
    found_post = make_post(other_user, post_type='FOUND', category='WALLET', color='BLACK', location='SUNGSHIN')
    update_matches(found_post)
    assert Match.objects.filter(lost=lost_post, found=found_post).exists()

    status_url = reverse('post-update-status', args=[found_post.id])

    # 1. 비로그인 차단 (401)
    assert api_client.patch(status_url, {'status': 'RETURNED'}, format='json').status_code == 401

    # 2. 작성자가 아닌 사용자 차단 (403)
    api_client.force_authenticate(user)
    assert api_client.patch(status_url, {'status': 'RETURNED'}, format='json').status_code == 403

    # 3. 작성자가 반환완료(RETURNED)로 변경 -> 200 & 매칭 후보에서 즉시 제외
    api_client.force_authenticate(other_user)
    res_returned = api_client.patch(status_url, {'status': 'RETURNED'}, format='json')
    assert res_returned.status_code == 200
    assert res_returned.data['status'] == 'RETURNED'
    assert res_returned.data['status_display'] == '반환완료'
    assert not Match.objects.filter(lost=lost_post, found=found_post).exists()

    # 4. 다시 진행중/보관중(OPEN)으로 복구 -> 매칭 재성립
    res_open = api_client.patch(status_url, {'status': 'OPEN'}, format='json')
    assert res_open.status_code == 200
    assert res_open.data['status'] == 'OPEN'
    assert Match.objects.filter(lost=lost_post, found=found_post).exists()