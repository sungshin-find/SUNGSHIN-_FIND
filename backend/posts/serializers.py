from django.utils import timezone
from rest_framework import serializers

from .models import Post


class PostSerializer(serializers.ModelSerializer):
    # 화면에 바로 보여줄 수 있도록 코드값과 함께 한글 표시값도 내려줌
    post_type_display = serializers.CharField(source='get_post_type_display', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    color_display = serializers.CharField(source='get_color_display', read_only=True)
    location_display = serializers.CharField(source='get_location_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    # 작성자는 요청한 사용자로 자동 지정 (클라이언트가 보낸 값은 무시)
    author = serializers.SerializerMethodField()
    is_mine = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id',
            'post_type', 'post_type_display',
            'title',
            'category', 'category_display',
            'color', 'color_display',
            'location', 'location_display',
            'location_detail',
            'event_date',
            'description',
            'status', 'status_display',
            'author', 'is_mine',
            'created_at', 'updated_at',
        ]
        # 반환 상태 변경은 #23 에서 별도 API 로 처리
        read_only_fields = ['status', 'created_at', 'updated_at']

    def get_author(self, obj):
        # #14 커스텀 User 가 들어와도 깨지지 않도록 get_username() 사용
        return obj.author.get_username()

    def get_is_mine(self, obj):
        request = self.context.get('request')
        return bool(request and request.user.is_authenticated and obj.author_id == request.user.id)

    def validate_event_date(self, value):
        if value > timezone.localdate():
            raise serializers.ValidationError('분실/습득 날짜는 오늘 이후일 수 없어요.')
        return value


class MatchCandidateSerializer(serializers.Serializer):
    """게시물 상세 화면의 "비슷한 게시물" 목록 한 줄 (#21)"""

    post = PostSerializer(read_only=True)
    score = serializers.IntegerField(read_only=True)
    reasons = serializers.ListField(child=serializers.CharField(), read_only=True)
