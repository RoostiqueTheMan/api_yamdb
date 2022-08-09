import uuid

from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from reviews.models import User, Category, Genre, Title, Review, Comment
from .utils import send_confirm
from .validators import (UsernameIsNotMeValidator, UserExistsValidator,
                         ConfirmCodeExistsValidator)


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        exclude = ('id',)


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        exclude = ('id',)


class TitleReadSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(
        read_only=True,
        many=True
    )
    rating = serializers.IntegerField()

    class Meta:
        fields = ('id', 'name', 'year', 'rating',
                  'description', 'genre', 'category')
        model = Title


class TitleWriteSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True
    )

    class Meta:
        fields = ('id', 'name', 'year', 'description',
                  'genre', 'category')
        model = Title


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        read_only_fields = ('title',)

    def validate_score(self, value):
        if not 1 <= value <= 10:
            raise serializers.ValidationError(
                "Должно быть целое число в диапазоне от 1 до 10."
            )
        return value

    def validate(self, data):
        title_id = self.context['view'].kwargs.get('title_id')
        user = self.context['request'].user
        is_review_exists = Review.objects.filter(
            title=title_id,
            author=user
        ).exists()
        if self.context['request'].method == 'POST' and is_review_exists:
            raise serializers.ValidationError('Второй отзыв оставить нельзя.')
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
        read_only_fields = ('review',)


class SignUpSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=150,
        required=True,
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            UsernameIsNotMeValidator(),
        ]
    )
    email = serializers.EmailField(
        max_length=254,
        required=True,
        validators=[
            UniqueValidator(queryset=User.objects.all()),
        ]
    )

    def create(self, validated_data):
        validated_data['confirm_code'] = str(uuid.uuid4())
        user = User.objects.create(**validated_data)
        send_confirm(user)
        return user


class SignInSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=150,
        required=True,
        validators=[
            UserExistsValidator()
        ]
    )
    email = serializers.EmailField(
        max_length=254,
        required=True,
        validators=[
            UserExistsValidator()
        ]
    )

    def create(self, validated_data):
        username = validated_data.get('username')
        email = validated_data.get('email')
        user = User.objects.get(
            username=username,
            email=email
        )
        send_confirm(user)
        return user


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=150,
        required=True,
        validators=[
            UserExistsValidator()
        ]
    )
    confirm_code = serializers.CharField(
        max_length=254,
        required=True,
        validators=[
            ConfirmCodeExistsValidator()
        ]
    )

    def validate(self, data):
        username = data.get('username')
        confirm_code = data.get('confirm_code')
        is_user_exists = User.objects.filter(
            username=username,
            confirm_code=confirm_code
        ).exists()
        if self.context['request'].method == 'POST' and (not is_user_exists):
            raise serializers.ValidationError(
                f'Пользователя с username=\'{username}\' не существует'
                f'или неверно указан confirm_code=\'{confirm_code}\' '
            )
        return data


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=150,
        required=True,
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            UsernameIsNotMeValidator(),
        ]
    )
    email = serializers.EmailField(
        max_length=254,
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role',)

    def update(self, instance, validated_data):
        if (instance.role == User.USER) and ('role' in validated_data):
            validated_data['role'] = User.USER
        return super().update(instance, validated_data)
