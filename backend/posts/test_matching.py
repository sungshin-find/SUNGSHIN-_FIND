"""매칭 알고리즘 테스트 (#21)"""

import datetime
from types import SimpleNamespace

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

from .choices import Category, Color, Location
from .matching import MATCH_THRESHOLD, score_pair, update_matches
from .models import Match, Post

TODAY = datetime.date(2026, 11, 20)


def fake(post_type='LOST', category='WALLET', color='BLACK', location='SUNGSHIN', days=0):
    """DB 없이 점수만 계산할 때 쓰는 가짜 게시물"""
    return SimpleNamespace(
        post_type=post_type,
        category=category,
        color=color,
        location=location,
        event_date=TODAY + datetime.timedelta(days=days),
        get_category_display=lambda: Category(category).label,
        get_color_display=lambda: Color(color).label,
        get_location_display=lambda: Location(location).label,
    )


# ---------------------------------------------------------------------------
# 점수 계산 단위 테스트 (DB 불필요)
# ---------------------------------------------------------------------------

def test_perfect_match_is_100():
    result = score_pair(fake('LOST'), fake('FOUND'))
    assert result.score == 100
    assert len(result.reasons) == 4


def test_different_category_is_excluded():
    assert score_pair(fake('LOST', category='WALLET'), fake('FOUND', category='PHONE')) is None


def test_etc_category_gets_partial_score():
    result = score_pair(fake('LOST', category='ETC'), fake('FOUND', category='WALLET'))
    assert result.score == 15 + 25 + 20 + 15


def test_both_etc_is_not_treated_as_same():
    # 둘 다 '기타'면 "같은 종류/색"이 아니라 "확인 필요" 부분 점수만 받아야 함
    result = score_pair(
        fake('LOST', category='ETC', color='ETC'),
        fake('FOUND', category='ETC', color='ETC'),
    )
    assert result.score == 15 + 8 + 20 + 15
    assert not any('같은 종류' in r or '같은 색상' in r for r in result.reasons)


def test_similar_color_gets_partial_score():
    same = score_pair(fake('LOST', color='BLACK'), fake('FOUND', color='BLACK')).score
    similar = score_pair(fake('LOST', color='BLACK'), fake('FOUND', color='NAVY')).score
    different = score_pair(fake('LOST', color='BLACK'), fake('FOUND', color='PINK')).score
    assert same > similar > different
    assert same - similar == 25 - 12


def test_location_scores():
    same = score_pair(fake('LOST', location='SUNGSHIN'), fake('FOUND', location='SUNGSHIN')).score
    campus = score_pair(fake('LOST', location='SUNGSHIN'), fake('FOUND', location='NANHYANG')).score
    vague = score_pair(fake('LOST', location='SUNGSHIN'), fake('FOUND', location='OUTDOOR')).score
    far = score_pair(fake('LOST', location='SUNGSHIN'), fake('FOUND', location='GREEN_CAMPUS')).score
    assert same > campus > vague > far


def test_same_vague_location_is_not_same_building():
    # 둘 다 '기타' 라고 해서 같은 건물로 보면 안 됨
    result = score_pair(fake('LOST', location='ETC'), fake('FOUND', location='ETC'))
    assert result.score == 40 + 25 + 5 + 15


@pytest.mark.parametrize('days, expected', [(0, 15), (1, 15), (3, 10), (7, 5), (10, 0), (-1, 15)])
def test_date_scores(days, expected):
    result = score_pair(fake('LOST'), fake('FOUND', days=days))
    assert result.score == 40 + 25 + 20 + expected


def test_found_long_before_lost_is_excluded():
    # 잃어버리기 이틀 전에 주운 물건은 같은 물건일 수 없음
    assert score_pair(fake('LOST'), fake('FOUND', days=-2)) is None


def test_same_category_only_is_below_threshold():
    # 종류만 같고 나머지가 다 다르면 후보로 띄우지 않음
    result = score_pair(
        fake('LOST', color='BLACK', location='SUNGSHIN'),
        fake('FOUND', color='PINK', location='GREEN_CAMPUS', days=20),
    )
    assert result.score == 40
    assert result.score < MATCH_THRESHOLD


# ---------------------------------------------------------------------------
# DB / API 테스트
# ---------------------------------------------------------------------------

@pytest.fixture
def users():
    User = get_user_model()
    return (
        User.objects.create_user(username='loser', password='pass1234!'),
        User.objects.create_user(username='finder', password='pass1234!'),
    )


def make_post(author, post_type, **fields):
    data = {
        'title': '테스트 게시물',
        'category': 'WALLET',
        'color': 'BLACK',
        'location': 'SUNGSHIN',
        'event_date': TODAY,
    }
    data.update(fields)
    return Post.objects.create(author=author, post_type=post_type, **data)


@pytest.mark.django_db
def test_update_matches_saves_candidates(users):
    loser, finder = users
    lost = make_post(loser, 'LOST')
    good = make_post(finder, 'FOUND')
    make_post(finder, 'FOUND', category='PHONE')  # 종류 다름 -> 제외

    created = update_matches(lost)

    assert [m.found for m in created] == [good]
    assert Match.objects.get().score == 100


@pytest.mark.django_db
def test_own_posts_and_returned_posts_are_not_matched(users):
    loser, finder = users
    lost = make_post(loser, 'LOST')
    make_post(loser, 'FOUND')                       # 자기 글
    make_post(finder, 'FOUND', status='RETURNED')   # 이미 반환됨

    assert update_matches(lost) == []


@pytest.mark.django_db
def test_recalculation_replaces_old_matches(users):
    loser, finder = users
    lost = make_post(loser, 'LOST')
    make_post(finder, 'FOUND')
    update_matches(lost)
    assert Match.objects.count() == 1

    lost.category = 'PHONE'
    lost.save()
    update_matches(lost)
    assert Match.objects.count() == 0


@pytest.mark.django_db
def test_recalculation_returns_only_new_matches(users):
    # 제목만 수정하는 경우: 같은 매칭이 "새 매칭"으로 다시 잡히면 알림이 중복됨
    loser, finder = users
    lost = make_post(loser, 'LOST')
    make_post(finder, 'FOUND')

    first = update_matches(lost)
    match_id = first[0].id

    lost.title = '제목만 수정'
    lost.save()
    assert update_matches(lost) == []                 # 새로 생긴 매칭 없음
    assert Match.objects.get().id == match_id         # 기존 행이 그대로 유지


@pytest.mark.django_db
def test_recalculation_updates_score_without_new_match(users):
    loser, finder = users
    lost = make_post(loser, 'LOST', color='BLACK')
    make_post(finder, 'FOUND', color='BLACK')
    update_matches(lost)
    assert Match.objects.get().score == 100

    lost.color = 'NAVY'  # 비슷한 색으로 수정 -> 점수만 바뀜
    lost.save()
    assert update_matches(lost) == []
    assert Match.objects.get().score == 100 - 25 + 12


@pytest.mark.django_db
def test_create_via_api_calculates_matches_for_both_sides(users):
    loser, finder = users
    client = APIClient()

    client.force_authenticate(loser)
    lost_id = client.post(reverse('post-list'), {
        'post_type': 'LOST', 'title': '검정 지갑 잃어버렸어요', 'category': 'WALLET',
        'color': 'BLACK', 'location': 'SUNGSHIN', 'event_date': str(TODAY),
    }, format='json').data['id']

    client.force_authenticate(finder)
    found_id = client.post(reverse('post-list'), {
        'post_type': 'FOUND', 'title': '남색 지갑 주웠어요', 'category': 'WALLET',
        'color': 'NAVY', 'location': 'SUNGSHIN', 'event_date': str(TODAY + datetime.timedelta(days=2)),
    }, format='json').data['id']

    # 습득물 등록만으로 분실물 쪽에서도 후보가 보여야 함
    response = client.get(reverse('post-matches', args=[lost_id]))
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]['post']['id'] == found_id
    assert response.data[0]['score'] == 40 + 12 + 20 + 10
    assert any('비슷한 색상' in reason for reason in response.data[0]['reasons'])

    response = client.get(reverse('post-matches', args=[found_id]))
    assert response.data[0]['post']['id'] == lost_id
