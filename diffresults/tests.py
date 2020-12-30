from django.test import TestCase, Client
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.urls import reverse

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

    def test_url_get_commits(self):
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

        url = create_url('TestMe', 'http://localhost:8888/', fetch_frequency=models.Url.DAILY)
        url.save()
        url.fetch()
        test_server_response = b'test2'
        url.fetch()

        self.assertEqual(len(url.get_commits()), 2)
        test_server_response = b'test3'
        url.fetch()
        self.assertEqual(len(url.get_commits()), 3)

        httpd.shutdown()

    def test_url_get_diff_good(self):
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

        url = create_url('TestMe', 'http://localhost:8888/', fetch_frequency=models.Url.DAILY)
        url.save()
        url.fetch()
        test_server_response = b'test2'
        url.fetch()
        httpd.shutdown()

        commits = url.get_commits()
        diff = url.get_diff(commits[1], commits[0])

        self.assertIn('+test2', diff)
        self.assertIn('-test1', diff)

    def test_url_get_diff_commit_not_related(self):
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

        url1 = create_url('TestMe', 'http://localhost:8888/', fetch_frequency=models.Url.DAILY)
        url1.save()
        url1.fetch()
        commits1 = url1.get_commits()
        url2 = create_url('TestMe', 'http://localhost:8888/', fetch_frequency=models.Url.DAILY)
        url2.save()
        url2.fetch()
        commits2 = url2.get_commits()
        httpd.shutdown()

        self.assertRaises(AssertionError, url1.get_diff, commits2[0], commits1[0])

    def test_url_get_commit_from_sha_good(self):
        url = create_url('TestMe', 'https://www.example.com/')
        url.save()
        url.fetch()
        commit = url.get_commits()[0]
        test_commit = url.get_commit_from_sha(commit.hexsha)

        self.assertEqual(commit, test_commit)

    def test_url_get_commit_from_sha_wrong_sha(self):
        url = create_url('TestMe', 'https://www.example.com/')
        url.save()
        url.fetch()
        wrong_sha = '2fd4e1c67a2d28fced849ee1bb76e7391b93eb12'
        test_commit = url.get_commit_from_sha(wrong_sha)

        self.assertIs(test_commit, None)


class TestUrlDashboard(TestCase):
    def setUp(self):
        models.Project.objects.create(project_name='TestMyView')

    def test_get_one_commit(self):
        client = Client()
        url = create_url('TestMyView', 'https://www.example.com/')
        url.save()
        response = client.get(reverse('diffresults:url', args=(url.pk,)))

        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.context['diff']), 0)
        self.assertEquals(len(response.context['commits']), 1)

    def test_get_nonexisting_url(self):
        client = Client()
        response = client.get(reverse('diffresults:url', args=(99999,)))

        self.assertEquals(response.status_code, 404)

    def test_get_invalid_hashes(self):
        test_server_response = b'test1'

        class TestRequestHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.end_headers()
                self.wfile.write(test_server_response)

        server_address = ('127.0.0.1', 8989)
        httpd = ThreadingHTTPServer(server_address, TestRequestHandler)

        def start_test_server():
            httpd.serve_forever()

        daemon1 = threading.Thread(name='daemon1', target=start_test_server)
        daemon1.start()

        url = create_url('TestMyView', 'http://localhost:8989/')
        url.save()
        url.fetch()
        test_server_response = b'test2'
        url.fetch()
        httpd.shutdown()

        client = Client()
        pk = url.id
        commits = url.get_commits()
        good_sha = commits[0].hexsha
        bad_sha = '2fd4e1c67a2d28fced849ee1bb76e7391b93eb12'
        response1 = client.get(reverse('diffresults:url-with-args', args=(pk, bad_sha, good_sha)))
        response2 = client.get(reverse('diffresults:url-with-args', args=(pk, good_sha, bad_sha)))
        response3 = client.get(reverse('diffresults:url-with-args', args=(pk, bad_sha, bad_sha)))
        response4 = client.get(reverse('diffresults:url-with-args', args=(pk, '2fdkkk', bad_sha)))
        self.assertEquals(response1.status_code, 404)
        self.assertEquals(response2.status_code, 404)
        self.assertEquals(response3.status_code, 404)
        self.assertEquals(response4.status_code, 404)


class TestPushoverUtil(TestCase):
    def test_simple_message_sent_results_in_status_ok(self):
        response = utils.send_pushover('title', 'message')
        self.assertEquals(response.status_code, 200)
