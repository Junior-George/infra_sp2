from django.urls import include, path
# from rest_framework.authtoken import views
from rest_framework.routers import DefaultRouter

from .views import (TitleViewSet, GenreViewSet,
                    CategoryViewSet, ReviewViewSet, CommentViewSet,
                    UserViewSet, create_user, create_token)

router = DefaultRouter()
router.register('users', UserViewSet)
router.register('titles', TitleViewSet)
router.register('genres', GenreViewSet)
router.register('categories', CategoryViewSet)

router.register(
    'titles/(?P<title_id>\\d+)/reviews',
    ReviewViewSet,
    basename='review')
router.register(
    'titles/(?P<title_id>\\d+)/reviews/(?P<review_id>\\d+)/comments',
    CommentViewSet,
    basename='comment')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/signup/', create_user),
    path('auth/token/', create_token),
]
