"""매칭 알림 테스트 (#22)"""

import datetime

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

from posts.matching import update_matches
from posts.models import Match, Post

from .models import Notification
from .services import notify_matches

TODAY = datetime.date(2026, 11, 20)


@pytest.fixture
def users():
    User = get_user_model()
    return (
        User.objects.create_user(username='loser', password='pass1234!'),
        User.objects.create_user(username='finder', password='pass1234!'),
        User.objects.create_user(username='stranger', password='pass1234!'),
    )


def make_post(author, post_type, **fields):
    data = {
        'title': f'{post_type} 게시물',
        'category': 'WALLET',
        'color': 'BLACK',
        'location': 'SUNGSHIN',
        'event_date': TODAY,
    }
    data.update(fields)
    return Post.objects.create(author=author, post_type=post_type, **data)


def match_and_notify(post):
    update_matches(post)
    return notify_matches(post)


# ---------------------------------------------------------------------------
# 알림 생성 규칙
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_high_score_match_notifies_both_sides(users):
    loser, finder, _ = users
    make_post(loser, 'LOST')
    found = make_post(finder, 'FOUND')  # 100점

    created = match_and_notify(found)

    assert sorted(n.recipient.username for n in created) == ['finder', 'loser']
    loser_noti = Notification.objects.get(recipient=loser)
    assert loser_noti.other_post() == found


@pytest.mark.django_db
def test_match_below_notify_threshold_has_no_notification(users):
    loser, finder, _ = users
    make_post(loser, 'LOST')
    # 종류 40 + 색상 0 + 같은 건물 20 + 날짜 0 = 60점 -> 후보(50)는 되지만 알림(70)은 아님
    found = make_post(finder, 'FOUND', color='PINK', event_date=TODAY + datetime.timedelta(days=20))

    assert match_and_notify(found) == []
    assert Match.objects.get().score == 60
    assert Notification.objects.count() == 0


@pytest.mark.django_db
def test_editing_title_does_not_duplicate_notifications(users):
    loser, finder, _ = users
    lost = make_post(loser, 'LOST')
    make_post(finder, 'FOUND')
    match_and_notify(lost)
    assert Notification.objects.count() == 2

    lost.title = '제목만 수정'
    lost.save()
    assert match_and_notify(lost) == []
    assert Notification.objects.count() == 2


@pytest.mark.django_db
def test_score_rising_above_threshold_notifies(users):
    # 기존 매칭(60점)이 수정으로 70점 이상이 되면 "새 매칭"이 아니어도 알림이 가야 함
    loser, finder, _ = users
    lost = make_post(loser, 'LOST', color='PINK')
    make_post(finder, 'FOUND', event_date=TODAY + datetime.timedelta(days=20))
    assert match_and_notify(lost) == []

    lost.color = 'BLACK'  # 색상 일치 +25 -> 85점
    lost.save()
    created = match_and_notify(lost)
    assert len(created) == 2


@pytest.mark.django_db
def test_notification_removed_when_match_disappears(users):
    loser, finder, _ = users
    lost = make_post(loser, 'LOST')
    make_post(finder, 'FOUND')
    match_and_notify(lost)

    lost.category = 'PHONE'  # 종류가 달라져서 후보 탈락
    lost.save()
    match_and_notify(lost)
    assert Notification.objects.count() == 0


# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_notification_api_flow(users):
    loser, finder, stranger = users
    client = APIClient()

    client.force_authenticate(loser)
    lost_id = client.post(reverse('post-list'), {
        'post_type': 'LOST', 'title': '검정 지갑 잃어버렸어요', 'category': 'WALLET',
        'color': 'BLACK', 'location': 'SUNGSHIN', 'event_date': str(TODAY),
    }, format='json').data['id']

    client.force_authenticate(finder)
    found_id = client.post(reverse('post-list'), {
        'post_type': 'FOUND', 'title': '검정 지갑 주웠어요', 'category': 'WALLET',
        'color': 'BLACK', 'location': 'SUNGSHIN', 'event_date': str(TODAY),
    }, format='json').data['id']

    # 분실자: 습득물 등록만으로 알림이 와 있어야 함
    client.force_authenticate(loser)
    assert client.get(reverse('notification-unread-count')).data == {'unread_count': 1}

    data = client.get(reverse('notification-list')).data
    assert len(data) == 1
    noti = data[0]
    assert noti['my_post']['id'] == lost_id
    assert noti['other_post']['id'] == found_id
    assert noti['score'] == 100
    assert '습득물' in noti['message']
    assert noti['is_read'] is False

    # 읽음 처리
    response = client.post(reverse('notification-read', args=[noti['id']]))
    assert response.status_code == 200
    assert response.data['is_read'] is True
    assert client.get(reverse('notification-list'), {'unread': 'true'}).data == []

    # 다른 사람은 내 알림을 볼 수도, 읽음 처리할 수도 없음
    client.force_authenticate(stranger)
    assert client.get(reverse('notification-list')).data == []
    assert client.post(reverse('notification-read', args=[noti['id']])).status_code == 404

    # 습득자도 알림을 받고, 전부 읽음 처리 가능
    client.force_authenticate(finder)
    assert client.post(reverse('notification-read-all')).data == {'updated': 1}
    assert client.get(reverse('notification-unread-count')).data == {'unread_count': 0}


@pytest.mark.django_db
def test_notifications_require_login():
    client = APIClient()
    assert client.get(reverse('notification-list')).status_code in (401, 403)
    assert client.get(reverse('notification-unread-count')).status_code in (401, 403)
