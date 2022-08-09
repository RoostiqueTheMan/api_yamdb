from rest_framework import serializers, exceptions

from reviews.models import User


class UserExistsValidator:
    requires_context = True

    def __call__(self, value, serializer_field):
        if isinstance(serializer_field, serializers.EmailField):
            if not User.objects.filter(email=value).exists():
                raise serializers.ValidationError(
                    f'Пользователь с таким email=\'{value}\' не найден.'
                )
        elif not User.objects.filter(username=value).exists():
            raise exceptions.NotFound(
                f'Пользователь с таким username=\'{value}\' не найден.'
            )


class ConfirmCodeExistsValidator:
    requires_context = True

    def __call__(self, value, serializer_field):
        if not User.objects.filter(confirm_code=value).exists():
            raise serializers.ValidationError(
                f'Пользователь с таким confirm_code=\'{value}\' не найден.'
            )


class UsernameIsNotMeValidator:
    def __call__(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError('Недопустимое имя пользователя')
        return value
