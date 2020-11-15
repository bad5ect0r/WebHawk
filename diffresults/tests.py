from django.test import TestCase
from django.core.exceptions import ValidationError

from . import models


class UrlTestCase(TestCase):
    def setUp(self):
        models.Project.objects.create(project_name='TestMe')

    def test_invalid_url_raises_validationerror(self):
        project = models.Project.objects.get(project_name='TestMe')
        url = models.Url(project=project, full_url='asdfsadf')

        self.assertRaises(ValidationError, url.clean_fields)

    def test_ftp_url_raises_validationerror(self):
        project = models.Project.objects.get(project_name='TestMe')
        url = models.Url(project=project, full_url='ftp://www.example.com/test.txt')

        self.assertRaises(ValidationError, url.clean_fields)

    def test_http_url_okay(self):
        project = models.Project.objects.get(project_name='TestMe')
        url = models.Url(project=project, full_url='http://www.example.com/test.txt')
        url.clean_fields()

        self.assertEqual(url.full_url, 'http://www.example.com/test.txt')

    def test_https_url_okay(self):
        project = models.Project.objects.get(project_name='TestMe')
        url = models.Url(project=project, full_url='https://www.example.com/test.txt')
        url.clean_fields()

        self.assertEqual(url.full_url, 'https://www.example.com/test.txt')
