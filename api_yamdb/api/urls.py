from django.urls import include, path
from rest_framework import routers

from api.views import (
    CategoryViewSet, GenreViewSet,
    TitleViewSet, ReviewViewSet, CommentViewSet,
    SignUpView, UserTokenView, UserViewSet, SignInView
)

router_v1 = routers.DefaultRouter()
router_v1.register('users', UserViewSet, basename='users')
router_v1.register('categories', CategoryViewSet, basename='categories')
router_v1.register('genres', GenreViewSet, basename='genres')
router_v1.register('titles', TitleViewSet, basename='titles')
router_v1.register(r'titles/(?P<title_id>\d+)/reviews',
                   ReviewViewSet, basename='reviews')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet, basename='comments'
)

urlpatterns = [
    path('v1/auth/signup/', SignUpView.as_view(), name='users_signup'),
    path('v1/auth/signin/', SignInView.as_view(), name='users_signin'),
    path('v1/auth/token/', UserTokenView.as_view(), name='users_token'),
    path('v1/', include(router_v1.urls)),
]
