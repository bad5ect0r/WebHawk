from django.utils import timezone
from django.core.exceptions import ValidationError


def date_in_past(value):
    if value > timezone.now():
        raise ValidationError(
            '%(value) is a date in the future. This is not allowed.',
            params={'value': str(value)}
        )
