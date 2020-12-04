from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

import requests


class CustomURLValidator(URLValidator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __call__(self, value):
        super().__call__(value)

        try:
            requests.get(value)
        except requests.exceptions.ConnectionError:
            raise ValidationError(
                "%(value)s is not reachable.",
                params={'value': value}
            )


def date_in_past(value):
    if value > timezone.now():
        raise ValidationError(
            '%(value) is a date in the future. This is not allowed.',
            params={'value': str(value)}
        )
