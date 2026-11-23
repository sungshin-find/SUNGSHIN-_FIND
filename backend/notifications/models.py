from django.conf import settings
from django.db import models


class Notification(models.Model):
    """
    매칭 후보 인앱 알림 (#22)

    점수가 NOTIFY_THRESHOLD(70점) 이상인 매칭이 생기면
    분실물 작성자와 습득물 작성자에게 하나씩 만든다.
    """

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
    )
    # 매칭이 사라지면(게시물 삭제·반환완료·내용 수정으로 후보 탈락) 알림도 의미가 없으므로 같이 삭제
    match = models.ForeignKey(
        'posts.Match',
        on_delete=models.CASCADE,
        related_name='notifications',
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at', '-id']
        constraints = [
            # 같은 매칭으로 같은 사람에게 알림이 두 번 가지 않도록 DB 에서도 막음
            models.UniqueConstraint(fields=['recipient', 'match'], name='unique_recipient_match'),
        ]
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
        ]

    def __str__(self):
        return f'{self.recipient} <- match #{self.match_id}'

    def my_post(self):
        """알림 받는 사람 본인의 게시물"""
        match = self.match
        return match.lost if match.lost.author_id == self.recipient_id else match.found

    def other_post(self):
        """알림으로 안내할 상대방 게시물"""
        match = self.match
        return match.found if match.lost.author_id == self.recipient_id else match.lost
