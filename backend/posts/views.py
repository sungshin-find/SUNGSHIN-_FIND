from django.db.models import Q
from django.utils.dateparse import parse_date
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response

from notifications.services import notify_matches

from .choices import Category, Color, Location, PostStatus, PostType
from .matching import update_matches
from .models import Match, Post
from .permissions import IsAuthorOrReadOnly
from .serializers import MatchCandidateSerializer, PostSerializer, PostStatusSerializer


class PostViewSet(viewsets.ModelViewSet):
    """
    게시물 CRUD (#17)

    GET    /api/posts/            목록 (?type=LOST|FOUND, ?mine=true)
    POST   /api/posts/            등록 (로그인 필요)
    GET    /api/posts/{id}/       상세
    PATCH  /api/posts/{id}/       수정 (작성자만)
    DELETE /api/posts/{id}/       삭제 (작성자만)
    GET    /api/posts/{id}/matches/   매칭 후보 (#21, 점수 높은 순)
    """

    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def get_queryset(self):
        queryset = Post.objects.select_related('author')
        params = self.request.query_params

        post_type = self.request.query_params.get('type')
        if post_type in PostType.values:
            queryset = queryset.filter(post_type=post_type)

        # 키워드 검색 (제목, 상세 설명, 상세 장소) (#23)
        keyword = (params.get('q') or params.get('search') or '').strip()
        if keyword:
            queryset = queryset.filter(
                Q(title__icontains=keyword)
                | Q(description__icontains=keyword)
                | Q(location_detail__icontains=keyword)
            )

        # 종류 / 장소 / 상태 필터 (#23)
        category = params.get('category')
        if category in Category.values:
            queryset = queryset.filter(category=category)

        location = params.get('location')
        if location in Location.values:
            queryset = queryset.filter(location=location)

        post_status = params.get('status')
        if post_status in PostStatus.values:
            queryset = queryset.filter(status=post_status)

        # 날짜 필터 (단일 날짜 ?date=YYYY-MM-DD 또는 범위 ?date_from=...&date_to=...) (#23)
        exact_date = parse_date(params.get('date') or '')
        if exact_date:
            queryset = queryset.filter(event_date=exact_date)
        else:
            date_from = parse_date(params.get('date_from') or '')
            date_to = parse_date(params.get('date_to') or '')
            if date_from:
                queryset = queryset.filter(event_date__gte=date_from)
            if date_to:
                queryset = queryset.filter(event_date__lte=date_to)

        # 마이페이지용 "내 게시물"
        if self.request.query_params.get('mine') == 'true':
            if not self.request.user.is_authenticated:
                return queryset.none()  # 로그인 안 했으면 "내 글"이 없으므로 빈 목록
            queryset = queryset.filter(author=self.request.user)

        return queryset

    def perform_create(self, serializer):
        post = serializer.save(author=self.request.user)
        # 등록하자마자 반대 유형 게시물과 매칭 점수 계산 (#21) -> 70점 이상이면 알림 (#22)
        update_matches(post)
        notify_matches(post)

    def perform_update(self, serializer):
        post = serializer.save()
        # 종류·색상·장소·날짜가 바뀌면 점수도 달라지므로 다시 계산
        update_matches(post)
        notify_matches(post)

    @action(
        detail=True,
        methods=['patch'],
        url_path='status',
        permission_classes=[permissions.IsAuthenticated, IsAuthorOrReadOnly],
    )
    def update_status(self, request, pk=None):
        """보관중(OPEN) <-> 반환완료(RETURNED) 상태 변경 (#23)"""
        post = self.get_object()
        serializer = PostStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_status = serializer.validated_data['status']
        if post.status != new_status:
            post.status = new_status
            post.save(update_fields=['status', 'updated_at'])
            # 반환완료(RETURNED) 처리 시 기존 매칭 후보에서 제거, 진행중(OPEN) 복귀 시 재매칭 (#23)
            created_matches = update_matches(post)
            if new_status == PostStatus.OPEN and created_matches:
                notify_matches(post)

        return Response(PostSerializer(post, context={'request': request}).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], permission_classes=[permissions.AllowAny])
    def matches(self, request, pk=None):
        post = self.get_object()
        if post.post_type == PostType.LOST:
            rows = Match.objects.filter(lost=post).select_related('found__author')
            candidates = [{'post': m.found, 'score': m.score, 'reasons': m.reasons} for m in rows]
        else:
            rows = Match.objects.filter(found=post).select_related('lost__author')
            candidates = [{'post': m.lost, 'score': m.score, 'reasons': m.reasons} for m in rows]

        serializer = MatchCandidateSerializer(candidates, many=True, context={'request': request})
        return Response(serializer.data)


def _to_list(choices):
    return [{'value': value, 'label': label} for value, label in choices.choices]


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def post_choices(request):
    """프론트 등록 폼의 선택지(드롭다운)를 서버 기준으로 내려줌"""
    return Response({
        'post_type': _to_list(PostType),
        'category': _to_list(Category),
        'color': _to_list(Color),
        'location': _to_list(Location),
        'status': _to_list(PostStatus),
    })
