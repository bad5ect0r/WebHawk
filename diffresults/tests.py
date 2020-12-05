from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone

from . import models, utils
from django_q.models import Schedule

from uuid import uuid4
from datetime import timedelta
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

import threading
import time


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

    def test_unreachable_url_raises_validationerror(self):
        url = create_url('TestMe', 'http://idontexistidontknowhy.com')

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
        future_last_fetch = timezone.now() + timedelta(days=10)
        url = create_url('TestMe', 'https://www.example.com/')
        url.last_fetched_date = future_last_fetch

        self.assertRaises(ValidationError, url.clean_fields)

    def test_fetch_url_on_save(self):
        url = create_url('TestMe', 'https://www.example.com/')
        url.save()
        content = b''

        with open(url.get_full_filepath(), 'rb') as fread:
            content = fread.read()

        self.assertIn(b'Example Domain', content)

    def test_change_being_tracked(self):
        test_server_response = b'test1'

        class TestRequestHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.end_headers()
                self.wfile.write(test_server_response)

        server_address = ('127.0.0.1', 8888)
        httpd = ThreadingHTTPServer(server_address, TestRequestHandler)

        def start_test_server():
            httpd.serve_forever()

        daemon1 = threading.Thread(name='daemon1', target=start_test_server)
        daemon1.start()
        url = create_url('TestMe', 'http://localhost:8888/')
        time.sleep(3)
        url.fetch()
        test_server_response = b'test2'
        url.fetch()
        httpd.shutdown()

        project = models.Project.objects.get(project_name='TestMe')
        repo = project.get_repo()
        commit_list = list(repo.iter_commits())

        self.assertEqual(len(commit_list), 2)

    def test_fetch_updates_last_fetched_date(self):
        url = create_url('TestMe', 'https://www.example.com')
        url.save()
        old_fetch_date = url.last_fetched_date
        time.sleep(5)
        url.fetch()

        self.assertNotEqual(url.last_fetched_date, old_fetch_date)

    def test_url_save_creates_scheduled_task(self):
        url = create_url('TestMe', 'https://www.example.com')
        url.save()
        self.assertIsInstance(url.schedule, Schedule)

    def test_url_fetch_frequency_matches_schedule(self):
        url = create_url('TestMe', 'https://www.example.com', fetch_frequency=models.Url.DAILY)
        url.save()
        day_minutes = models.Url.DAILY.total_seconds() / 60
        self.assertEquals(url.schedule.minutes, day_minutes)

    def test_url_fetch_frequency_update_updates_schedule(self):
        url = create_url('TestMe', 'https://www.example.com', fetch_frequency=models.Url.DAILY)
        url.save()
        old_minutes = url.schedule.minutes
        old_next_run = url.schedule.next_run

        url.fetch_frequency = models.Url.ONE_MINUTE
        url.save()
        new_minutes = url.schedule.minutes
        new_next_run = url.schedule.next_run

        self.assertNotEqual(new_minutes, old_minutes)
        self.assertNotEqual(new_next_run, old_next_run)


class TestPushoverUtil(TestCase):
    def test_simple_message_sent_results_in_status_ok(self):
        response = utils.send_pushover('title', 'message')
        self.assertEquals(response.status_code, 200)
