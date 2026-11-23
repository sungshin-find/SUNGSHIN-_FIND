from django.conf import settings
from django.db import models

from .choices import Category, Color, Location, PostStatus, PostType


class Post(models.Model):
    """분실물 / 습득물 게시물 (#17)"""

    post_type = models.CharField('유형', max_length=10, choices=PostType.choices)
    title = models.CharField('제목', max_length=100)

    # 매칭(#21)에 쓰이는 표준화 필드
    category = models.CharField('물건 종류', max_length=20, choices=Category.choices)
    color = models.CharField('색상', max_length=20, choices=Color.choices)
    location = models.CharField('장소(건물)', max_length=20, choices=Location.choices)
    event_date = models.DateField('분실/습득 날짜')

    # 매칭에는 쓰지 않는 자유 입력 필드
    location_detail = models.CharField('상세 장소', max_length=100, blank=True)
    description = models.TextField('상세 설명', blank=True)

    status = models.CharField(
        '상태', max_length=10, choices=PostStatus.choices, default=PostStatus.OPEN
    )

    # settings.AUTH_USER_MODEL 을 써야 #14 에서 커스텀 User 로 바뀌어도 그대로 동작함
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='작성자',
    )

    created_at = models.DateTimeField('작성일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            # 매칭할 때 "반대 유형 + 진행중 + 같은 종류" 로 후보를 좁히기 위한 인덱스
            models.Index(fields=['post_type', 'status', 'category']),
        ]

    def __str__(self):
        return f'[{self.get_post_type_display()}] {self.title}'
