from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PostViewSet, post_choices

router = DefaultRouter()
router.register('posts', PostViewSet, basename='post')

urlpatterns = [
    # router 의 posts/<pk>/ 보다 먼저 와야 함
    path('posts/choices/', post_choices, name='post-choices'),
    path('', include(router.urls)),
]
