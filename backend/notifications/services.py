"""
매칭 결과 -> 알림 생성 (#22)

게시물 등록·수정 때 posts.views 에서 update_matches(post) 다음에 호출한다.
"""

from django.db import transaction
from django.db.models import Q

from posts.matching import NOTIFY_THRESHOLD
from posts.models import Match

from .models import Notification


def notify_matches(post):
    """
    post 의 매칭 중 NOTIFY_THRESHOLD 이상인 것에 대해 양쪽 작성자에게 알림을 만든다.

    - update_matches() 가 돌려주는 "새 매칭"만 보지 않고, 현재 70점 이상인 매칭을 모두 확인한다.
      → 기존 매칭이 수정으로 60점 -> 75점이 되는 경우에도 알림이 가야 하기 때문
    - 이미 보낸 알림은 (recipient, match) 유니크 제약 + get_or_create 로 다시 만들지 않는다.
      → 제목만 고쳐도 알림이 또 가는 문제(#21 리뷰)가 생기지 않음

    반환: 이번에 새로 만든 Notification 목록
    """
    matches = (
        Match.objects.filter(Q(lost=post) | Q(found=post), score__gte=NOTIFY_THRESHOLD)
        .select_related('lost', 'found')
    )

    created = []
    with transaction.atomic():
        for match in matches:
            for recipient_id in (match.lost.author_id, match.found.author_id):
                notification, is_new = Notification.objects.get_or_create(
                    recipient_id=recipient_id, match=match,
                )
                if is_new:
                    created.append(notification)
    return created
