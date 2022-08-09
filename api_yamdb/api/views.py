import uuid

from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import (filters, viewsets, permissions,
                            status, views)
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.decorators import action

from reviews.models import User, Title, Genre, Category, Review
from .serializers import (CategorySerializer, GenreSerializer,
                          TitleReadSerializer, TitleWriteSerializer,
                          ReviewSerializer, CommentSerializer,
                          SignUpSerializer, UserSerializer,
                          TokenSerializer, SignInSerializer)
from .permissions import (SuperOrAdmin, AllReadOnlyAdminPostDel,
                          AdminModerAuthorReader)
from .filters import TitleFilter
from .utils import get_user_token
from .mixins import CreateListDestroyViewSet


class CategoryViewSet(CreateListDestroyViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (AllReadOnlyAdminPostDel,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenreViewSet(CreateListDestroyViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (AllReadOnlyAdminPostDel,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')
    ).order_by('name')
    permission_classes = (AllReadOnlyAdminPostDel,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleWriteSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (AdminModerAuthorReader,)

    def get_title(self):
        title_id = self.kwargs.get("title_id")
        return get_object_or_404(Title, pk=title_id)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())

    def get_queryset(self):
        return self.get_title().reviews.all()


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (AdminModerAuthorReader,)

    def get_review(self):
        title_id = self.kwargs.get("title_id")
        if get_object_or_404(Title, pk=title_id):
            pass
        review_id = self.kwargs.get("review_id")
        return get_object_or_404(Review, pk=review_id)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())

    def get_queryset(self):
        return self.get_review().comments.all()


class SignUpView(views.APIView):

    def post(self, request):
        signup_serializer = SignUpSerializer(data=request.data)

        signup_serializer.is_valid(raise_exception=True)
        signup_serializer.save()
        return Response(signup_serializer.data, status=status.HTTP_200_OK)


class SignInView(views.APIView):
    def post(self, request):
        signin_serializer = SignInSerializer(data=request.data)

        signin_serializer.is_valid(raise_exception=True)
        signin_serializer.save()
        message = {
            'message': ('Аутентификация прошла успешно, '
                        'проверьте ваш e-mail.'),
            'data': signin_serializer.data
        }
        return Response(message, status=status.HTTP_200_OK)


class UserTokenView(views.APIView):

    def post(self, request):
        token_serializer = TokenSerializer(data=request.data)

        token_serializer.is_valid(raise_exception=True)
        token_serializer.save()

        user = token_serializer.data.user
        user.confirm_code = str(uuid.uuid4())
        token = get_user_token(user)
        user.save()
        return Response(token, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('=username',)
    permission_classes = (SuperOrAdmin,)

    @action(
        detail=False,
        methods=['get', 'patch'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def me(self, request):
        if request.method == 'get':
            serializer = UserSerializer(request.user)
            return Response(serializer.data)

        serializer = UserSerializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
