from django.db import models
from django.contrib.auth.models import AbstractUser

from .validators import year_validator, score_validator


class User(AbstractUser):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'
    ROLE_CHOICES = [
        (USER, 'Пользователь'),
        (MODERATOR, 'Модератор'),
        (ADMIN, 'Администратор'),
    ]

    bio = models.TextField(blank=True)
    role = models.CharField(
        max_length=25,
        choices=ROLE_CHOICES,
        default=USER
    )
    confirm_code = models.CharField(max_length=254)

    class Meta:
        ordering = ('username',)

    @property
    def is_user(self):
        return self.role == self.USER

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    @property
    def is_admin(self):
        return self.role == self.ADMIN


class Category(models.Model):
    name = models.CharField('Название', max_length=256)
    slug = models.SlugField(unique=True, max_length=50)

    class Meta:
        verbose_name = 'Категории (типы) произведений'
        verbose_name_plural = verbose_name
        ordering = ['name']

    def __str__(self) -> str:
        return self.name[:20]


class Genre(models.Model):
    name = models.CharField('Название', max_length=256)
    slug = models.SlugField(unique=True, max_length=50)

    class Meta:
        verbose_name = 'Жанры произведений'
        verbose_name_plural = verbose_name
        ordering = ['name']

    def __str__(self) -> str:
        return self.name[:20]


class Title(models.Model):
    name = models.CharField('Название', max_length=256)
    year = models.PositiveSmallIntegerField(
        'Год издания',
        validators=[year_validator],
        help_text='Год издания произведения.'
    )
    description = models.TextField('Описание', blank=True, null=True)
    genre = models.ManyToManyField(
        Genre,
        related_name='titles'
    )
    category = models.ForeignKey(
        Category,
        related_name='titles',
        on_delete=models.SET_NULL,
        help_text='Категория произведения.',
        null=True
    )

    class Meta:
        verbose_name = 'Произведения'
        verbose_name_plural = verbose_name
        ordering = ['name']

    def __str__(self) -> str:
        return self.name[:20]

    def get_rating(self):
        return self.reviews.aggregate(models.Avg('score'))['score__avg']


class Review(models.Model):
    text = models.TextField(
        'Текст отзыва',
        help_text='Введите текст отзыва')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор')
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    score = models.IntegerField(
        'Оценка',
        validators=[score_validator],
        help_text='Введите оценку произведения.'
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        verbose_name = 'Отзывы'
        verbose_name_plural = verbose_name
        ordering = ['-pub_date']
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique review'
            )
        ]

    def __str__(self) -> str:
        return self.text[:20]


class Comment(models.Model):
    text = models.TextField(
        'Текст коментария',
        help_text='Введите текст коментария')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    pub_date = models.DateTimeField(
        'Дата добавления',
        auto_now_add=True,
        db_index=True)

    class Meta:
        verbose_name = 'Комментарии'
        verbose_name_plural = verbose_name
        ordering = ['pub_date']

    def __str__(self) -> str:
        return self.text[:20]
