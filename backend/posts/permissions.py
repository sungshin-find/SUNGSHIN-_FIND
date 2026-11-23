from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """조회는 누구나, 수정·삭제는 작성자만 가능"""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author_id == request.user.id
