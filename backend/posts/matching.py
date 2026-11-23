"""
규칙 기반 분실물 ↔ 습득물 매칭 (#21)

분실물(LOST) 하나와 습득물(FOUND) 하나를 비교해서 0~100점 사이의 유사도 점수를 매긴다.
점수 규칙과 가중치를 정한 이유는 docs/matching.md 에 정리했다.

    물건 종류  최대 40점   (다르면 후보에서 제외)
    색상       최대 25점
    장소       최대 20점
    날짜       최대 15점   (습득일이 분실일보다 많이 앞서면 제외)
"""

from dataclasses import dataclass, field

from .choices import Category, Color, Location, PostStatus, PostType

# ---------------------------------------------------------------------------
# 가중치 / 기준값 (바꿀 때는 docs/matching.md 도 같이 수정)
# ---------------------------------------------------------------------------

CATEGORY_SAME = 40
CATEGORY_ETC = 15          # 한쪽이 '기타' 라서 확신할 수 없는 경우

COLOR_SAME = 25
COLOR_SIMILAR = 12         # 같은 색 계열 (조명·사람마다 다르게 부르는 경우)
COLOR_ETC = 8

LOCATION_SAME = 20
LOCATION_SAME_CAMPUS = 8   # 같은 수정캠퍼스 안의 다른 건물
LOCATION_VAGUE = 5         # 한쪽이 '교내 야외' / '기타'

# (습득일 - 분실일) 일수 -> 점수
DATE_SCORES = [
    (1, 15),   # 0 ~ 1일
    (3, 10),   # 2 ~ 3일
    (7, 5),    # 4 ~ 7일
]
# 습득일이 분실일보다 이만큼 이상 앞서면 같은 물건일 수 없다고 판단 (입력 실수 1일 허용)
DATE_TOLERANCE_BEFORE = 1

# 이 점수 이상이면 매칭 후보로 저장 / 보여줌
MATCH_THRESHOLD = 50
# 이 점수 이상이면 알림을 보냄 (#22 에서 사용)
NOTIFY_THRESHOLD = 70

# 사람마다 다르게 부를 수 있는 비슷한 색 묶음
COLOR_GROUPS = [
    {Color.BLACK, Color.NAVY, Color.GRAY},
    {Color.WHITE, Color.BEIGE, Color.SILVER, Color.GRAY},
    {Color.BLUE, Color.NAVY},
    {Color.RED, Color.PINK, Color.ORANGE},
    {Color.YELLOW, Color.GOLD, Color.ORANGE, Color.BEIGE},
    {Color.BROWN, Color.BEIGE},
    {Color.PURPLE, Color.PINK},
    {Color.GREEN},
]

SUJEONG_CAMPUS = {
    Location.SUNGSHIN, Location.SUJEONG, Location.NANHYANG, Location.UNJEONG,
    Location.MUSIC, Location.FORMATIVE, Location.ADMIN,
}
VAGUE_LOCATIONS = {Location.OUTDOOR, Location.ETC}


@dataclass
class MatchResult:
    score: int
    reasons: list = field(default_factory=list)


def _category_score(lost, found):
    # '기타'는 "어떤 종류인지 모름"이라는 뜻이라, 둘 다 '기타'여도 같은 종류로 보지 않는다
    # 그래서 같은 값인지 비교하기 전에 '기타' 여부를 먼저 확인한다 (#21 리뷰 반영)
    if Category.ETC in (lost.category, found.category):
        return CATEGORY_ETC, '종류 확인 필요 (기타 포함)'
    if lost.category == found.category:
        return CATEGORY_SAME, f'같은 종류 ({lost.get_category_display()})'
    return None, None  # 종류가 다르면 같은 물건일 수 없음


def _color_score(lost, found):
    # 종류와 같은 이유로 '기타'를 먼저 확인
    if Color.ETC in (lost.color, found.color):
        return COLOR_ETC, '색상 확인 필요 (기타 포함)'
    if lost.color == found.color:
        return COLOR_SAME, f'같은 색상 ({lost.get_color_display()})'
    if any(lost.color in group and found.color in group for group in COLOR_GROUPS):
        return COLOR_SIMILAR, f'비슷한 색상 ({lost.get_color_display()}·{found.get_color_display()})'
    return 0, None


def _location_score(lost, found):
    if lost.location == found.location and lost.location not in VAGUE_LOCATIONS:
        return LOCATION_SAME, f'같은 장소 ({lost.get_location_display()})'
    if lost.location in SUJEONG_CAMPUS and found.location in SUJEONG_CAMPUS:
        return LOCATION_SAME_CAMPUS, '같은 수정캠퍼스'
    if lost.location in VAGUE_LOCATIONS or found.location in VAGUE_LOCATIONS:
        return LOCATION_VAGUE, '장소 확인 필요 (야외/기타 포함)'
    return 0, None


def _date_score(lost, found):
    diff = (found.event_date - lost.event_date).days
    if diff < -DATE_TOLERANCE_BEFORE:
        return None, None  # 잃어버리기 전에 주운 물건은 다른 물건
    diff = max(diff, 0)
    for max_days, score in DATE_SCORES:
        if diff <= max_days:
            return score, f'날짜 차이 {diff}일'
    return 0, None


def score_pair(lost, found):
    """
    분실물 1개 + 습득물 1개의 매칭 점수를 계산한다.
    같은 물건일 수 없는 조합이면 None 을 돌려준다.
    """
    total = 0
    reasons = []
    for scorer in (_category_score, _color_score, _location_score, _date_score):
        score, reason = scorer(lost, found)
        if score is None:
            return None
        total += score
        if reason:
            reasons.append(f'{reason} +{score}')
    return MatchResult(score=total, reasons=reasons)


def score_posts(post, other):
    """유형 순서와 상관없이 두 게시물의 점수를 계산"""
    if post.post_type == PostType.LOST:
        return score_pair(post, other)
    return score_pair(other, post)


def find_candidates(post):
    """
    post 와 매칭될 수 있는 반대 유형 게시물을 점수 높은 순으로 돌려준다.
    반환: [(상대 게시물, MatchResult), ...]
    """
    from .models import Post  # models 가 이 파일을 import 하므로 순환 참조 방지

    if post.status != PostStatus.OPEN:
        return []

    opposite = PostType.FOUND if post.post_type == PostType.LOST else PostType.LOST
    queryset = (
        Post.objects.filter(post_type=opposite, status=PostStatus.OPEN)
        .exclude(author_id=post.author_id)  # 자기 글끼리는 매칭하지 않음
        .select_related('author')
    )
    # DB 단계에서 종류로 먼저 걸러서 비교 횟수를 줄임 (인덱스 사용)
    if post.category != Category.ETC:
        queryset = queryset.filter(category__in=[post.category, Category.ETC])

    results = []
    for other in queryset:
        result = score_posts(post, other)
        if result and result.score >= MATCH_THRESHOLD:
            results.append((other, result))
    results.sort(key=lambda pair: pair[1].score, reverse=True)
    return results


def update_matches(post):
    """
    post 의 매칭 결과를 다시 계산해서 Match 테이블과 맞춘다.
    게시물 등록·수정 때, 그리고 반환완료 처리(#23) 때 호출한다.

    - 이미 있던 매칭이 그대로 유지되면 점수·근거만 갱신 (새 매칭으로 치지 않음)
    - 더 이상 후보가 아닌 매칭은 삭제
    - 처음 생긴 매칭만 새로 만든다

    반환: 이번에 "처음" 생긴 Match 목록 (#22 알림에서 사용)
          → 제목·설명만 수정했을 때 같은 사람에게 알림이 중복으로 가지 않음 (#21 리뷰 반영)
    """
    from django.db import transaction
    from django.db.models import Q

    from .models import Match

    with transaction.atomic():
        existing = {
            (m.lost_id, m.found_id): m
            for m in Match.objects.filter(Q(lost=post) | Q(found=post))
        }

        created = []
        for other, result in find_candidates(post):
            lost, found = (post, other) if post.post_type == PostType.LOST else (other, post)
            match = existing.pop((lost.id, found.id), None)

            if match is None:
                created.append(
                    Match.objects.create(
                        lost=lost, found=found, score=result.score, reasons=result.reasons
                    )
                )
            elif match.score != result.score or match.reasons != result.reasons:
                match.score = result.score
                match.reasons = result.reasons
                match.save(update_fields=['score', 'reasons'])

        # 남은 것 = 재계산 결과에 없는 매칭 → 삭제
        if existing:
            Match.objects.filter(pk__in=[m.pk for m in existing.values()]).delete()

    return created
