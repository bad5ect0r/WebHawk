from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone

from . import models

from uuid import uuid4
from datetime import timedelta


def create_url(project_name, url_text, *args, **kwargs):
    project = models.Project.objects.get(project_name=project_name)
    url = models.Url(
        project=project,
        url_name=str(uuid4()),
        full_url=url_text,
        *args,
        **kwargs
    )

    return url


class UrlTestCase(TestCase):
    def setUp(self):
        models.Project.objects.create(project_name='TestMe')

    def test_invalid_url_raises_validationerror(self):
        url = create_url('TestMe', 'asdfasdf')

        self.assertRaises(ValidationError, url.clean_fields)

    def test_ftp_url_raises_validationerror(self):
        url = create_url('TestMe', 'ftp://www.example.com/test.txt')

        self.assertRaises(ValidationError, url.clean_fields)

    def test_http_url_okay(self):
        url = create_url('TestMe', 'http://www.example.com/test.txt')
        url.clean_fields()

        self.assertEqual(url.full_url, 'http://www.example.com/test.txt')

    def test_https_url_okay(self):
        url = create_url('TestMe', 'https://www.example.com/test.txt')
        url.clean_fields()

        self.assertEqual(url.full_url, 'https://www.example.com/test.txt')

    def test_arbitrary_filename_fails_with_validation_error(self):
        url = create_url(
            'TestMe',
            'https://www.example.com/test.txt',
            filename='ddd'
        )

        self.assertRaises(ValidationError, url.clean_fields)

    def test_last_fetch_date_not_in_future(self):
        future_last_fetch = timezone.now() +  timedelta(days=10)
        url = create_url('TestMe', 'https://www.example.com/')
        url.last_fetched_date = future_last_fetch

        self.assertRaises(ValidationError, url.clean_fields)
