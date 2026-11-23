from rest_framework import serializers

from posts.choices import PostType

from .models import Notification


class NotificationPostSerializer(serializers.Serializer):
    """알림 카드에 필요한 게시물 요약 (상세는 /api/posts/{id}/ 로 이동)"""

    id = serializers.IntegerField()
    post_type = serializers.CharField()
    title = serializers.CharField()
    category_display = serializers.CharField(source='get_category_display')
    location_display = serializers.CharField(source='get_location_display')
    event_date = serializers.DateField()


class NotificationSerializer(serializers.ModelSerializer):
    score = serializers.IntegerField(source='match.score', read_only=True)
    reasons = serializers.ListField(source='match.reasons', child=serializers.CharField(), read_only=True)
    my_post = serializers.SerializerMethodField()
    other_post = serializers.SerializerMethodField()
    message = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ['id', 'message', 'score', 'reasons', 'my_post', 'other_post', 'is_read', 'created_at']
        read_only_fields = fields

    def get_my_post(self, obj):
        return NotificationPostSerializer(obj.my_post()).data

    def get_other_post(self, obj):
        return NotificationPostSerializer(obj.other_post()).data

    def get_message(self, obj):
        # 제목이 나중에 바뀌어도 최신 제목이 보이도록 저장하지 않고 매번 만든다
        mine = obj.my_post()
        other = obj.other_post()
        other_kind = '습득물' if other.post_type == PostType.FOUND else '분실물'
        return f"'{mine.title}'와(과) 비슷한 {other_kind}이 올라왔어요 ({obj.match.score}점)"
