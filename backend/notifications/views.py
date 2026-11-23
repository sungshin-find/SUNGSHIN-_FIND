from rest_framework import mixins, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    매칭 알림 (#22) - 로그인한 본인 알림만 보임

    GET  /api/notifications/                 목록 (?unread=true 면 안 읽은 것만)
    GET  /api/notifications/unread-count/    안 읽은 개수 (헤더 종 아이콘 배지용)
    POST /api/notifications/{id}/read/       하나 읽음 처리
    POST /api/notifications/read-all/        전부 읽음 처리
    """

    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # 남의 알림은 목록에도, {id}/read/ 에도 안 잡힘 (404)
        queryset = Notification.objects.filter(recipient=self.request.user).select_related(
            'match__lost', 'match__found'
        )
        if self.request.query_params.get('unread') == 'true':
            queryset = queryset.filter(is_read=False)
        return queryset

    @action(detail=False, methods=['get'], url_path='unread-count')
    def unread_count(self, request):
        count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        return Response({'unread_count': count})

    @action(detail=True, methods=['post'])
    def read(self, request, pk=None):
        notification = self.get_object()
        if not notification.is_read:
            notification.is_read = True
            notification.save(update_fields=['is_read'])
        return Response(self.get_serializer(notification).data)

    @action(detail=False, methods=['post'], url_path='read-all')
    def read_all(self, request):
        updated = Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        return Response({'updated': updated})
