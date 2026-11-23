from rest_framework import permissions, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response

from .choices import Category, Color, Location, PostStatus, PostType
from .matching import update_matches
from .models import Match, Post
from .permissions import IsAuthorOrReadOnly
from .serializers import MatchCandidateSerializer, PostSerializer


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

        post_type = self.request.query_params.get('type')
        if post_type in PostType.values:
            queryset = queryset.filter(post_type=post_type)

        # 마이페이지용 "내 게시물"
        if self.request.query_params.get('mine') == 'true':
            if not self.request.user.is_authenticated:
                return queryset.none()  # 로그인 안 했으면 "내 글"이 없으므로 빈 목록
            queryset = queryset.filter(author=self.request.user)

        return queryset

    def perform_create(self, serializer):
        post = serializer.save(author=self.request.user)
        # 등록하자마자 반대 유형 게시물과 매칭 점수 계산 (#21)
        update_matches(post)

    def perform_update(self, serializer):
        post = serializer.save()
        # 종류·색상·장소·날짜가 바뀌면 점수도 달라지므로 다시 계산
        update_matches(post)

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
