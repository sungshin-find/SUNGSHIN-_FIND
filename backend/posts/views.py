from rest_framework import permissions, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .choices import Category, Color, Location, PostStatus, PostType
from .models import Post
from .permissions import IsAuthorOrReadOnly
from .serializers import PostSerializer


class PostViewSet(viewsets.ModelViewSet):
    """
    게시물 CRUD (#17)

    GET    /api/posts/            목록 (?type=LOST|FOUND, ?mine=true)
    POST   /api/posts/            등록 (로그인 필요)
    GET    /api/posts/{id}/       상세
    PATCH  /api/posts/{id}/       수정 (작성자만)
    DELETE /api/posts/{id}/       삭제 (작성자만)
    """

    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def get_queryset(self):
        queryset = Post.objects.select_related('author')

        post_type = self.request.query_params.get('type')
        if post_type in PostType.values:
            queryset = queryset.filter(post_type=post_type)

        # 마이페이지용 "내 게시물"
        if self.request.query_params.get('mine') == 'true' and self.request.user.is_authenticated:
            queryset = queryset.filter(author=self.request.user)

        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


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
