from django.utils import timezone
from django.core.exceptions import ValidationError

import requests


def date_in_past(value):
    if value > timezone.now():
        raise ValidationError(
            '%(value) is a date in the future. This is not allowed.',
            params={'value': str(value)}
        )


def url_not_reachable(value):
    try:
        requests.get(value)
    except requests.exceptions.ConnectionError:
        raise ValidationError(
            "%(value)s is not reachable.",
            params={'value': value}
        )
