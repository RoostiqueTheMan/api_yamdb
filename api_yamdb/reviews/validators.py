from django.utils import timezone

from django.core.exceptions import ValidationError


def year_validator(value: int):
    if value < 1900 or value > timezone.now().year:
        raise ValidationError(
            f'{value} не корректный год!',
            params={'value': value},
        )


def score_validator(value: int):
    if value < 1 or value > 10:
        raise ValidationError(
            f'{value} не корректная оценка!',
            params={'value': value},
        )
