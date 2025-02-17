from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils import timezone

from . import utils, validators

from urllib.parse import urlparse
from pathlib import PosixPath
from git import Repo

import requests
import datetime
import uuid


class Project(models.Model):
    project_name = models.CharField('name', max_length=256)
    create_date = models.DateTimeField('date created', auto_now_add=True)
    git_dir = models.FilePathField('git directory', path=str(settings.GIT_DIR), editable=False)

    def __str__(self):
        return self.project_name

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.git_dir = settings.GIT_DIR / str(uuid.uuid4())
            utils.create_gitdir(self.git_dir)

        return super().save(*args, **kwargs)

    def get_repo(self):
        return Repo(self.git_dir)

    def import_urls_from_file(self, uploaded_file):
        bad_line_urls = []
        good_urls = []

        for line_no, line in enumerate(uploaded_file):
            line_no += 1
            line = line.strip().decode('ascii')
            url_parsed = urlparse(line)
            url_name = 'Unnamed uploaded item'

            url = Url(
                project=self,
                url_name=url_name,
                full_url=url_parsed.geturl()
            )

            try:
                url.clean_fields()
            except ValidationError as e:
                bad_line_urls.append((line_no, line, e))
            else:
                good_urls.append(url)

        if len(bad_line_urls) == 0:
            for url in good_urls:
                url.save()

        return bad_line_urls


class Url(models.Model):
    WEEKLY = datetime.timedelta(days=7)
    DAILY = datetime.timedelta(days=1)
    SIX_HOURS = datetime.timedelta(hours=6)
    HOURLY = datetime.timedelta(hours=1)
    HALF_HOURLY = datetime.timedelta(minutes=30)
    FIVE_MINUTES = datetime.timedelta(minutes=5)
    ONE_MINUTE = datetime.timedelta(minutes=1)

    FETCH_FREQUENCIES = {
        (WEEKLY, 'Weekly'),
        (DAILY, 'Daily'),
        (SIX_HOURS, 'Six hours, every day'),
        (HOURLY, 'Hourly'),
        (HALF_HOURLY, 'Every half hour'),
        (FIVE_MINUTES, 'Every five minutes'),
        (ONE_MINUTE, 'Every minute')
    }

    FILE_EXTENSIONS = {
        ('js', 'js'),
        ('html', 'html'),
        ('xml', 'xml'),
        ('txt', 'txt'),
    }

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    url_name = models.CharField('name', max_length=256)
    method = models.CharField('http method', max_length=256, default='GET')
    full_url = models.CharField(max_length=2048, validators=[validators.CustomURLValidator(['http', 'https'])])
    body = models.TextField('request body', blank=True, default='')
    fetch_frequency = models.DurationField('fetch frequency', choices=FETCH_FREQUENCIES, default=DAILY)
    filename = models.UUIDField('filename', editable=False, default=uuid.uuid4)
    file_ext = models.CharField('file extension', choices=FILE_EXTENSIONS, max_length=16, default='txt')
    add_date = models.DateTimeField(
        'date added',
        validators=[validators.date_in_past],
        auto_now_add=True
    )
    last_fetched_date = models.DateTimeField(
        'date last fetched',
        null=True,
        validators=[validators.date_in_past],
        editable=False
    )

    def __str__(self):
        return self.full_url

    def domain(self):
        url_parsed = urlparse(self.full_url)
        return url_parsed.hostname

    def get_headers(self):
        headers = {}

        for header in self.header_set.all():
            headers[header.header_name] = header.header_value

        return headers

    def get_full_filename(self):
        return '{}.{}'.format(self.filename, self.file_ext)

    def get_full_filepath(self):
        return PosixPath(self.project.git_dir) / self.get_full_filename()

    def do_request(self):
        headers = self.get_headers()
        resp = requests.request(self.method, self.full_url, data=self.body, headers=headers)

        return resp

    def save_into_file(self, data):
        with open(self.get_full_filepath(), 'wb') as fwrite:
            fwrite.write(data)

    def is_file_untracked(self):
        repo = self.project.get_repo()

        return self.get_full_filename() in repo.untracked_files

    def is_file_different(self):
        if self.is_file_untracked():
            return True

        repo = self.project.get_repo()

        for diff in repo.index.diff(None):
            if diff.a_path == self.get_full_filename():
                return True

        return False

    def commit(self, commit_msg):
        repo = self.project.get_repo()
        repo.index.add([self.get_full_filename()])
        repo.index.commit(commit_msg)

    def fetch(self, do_save=True):
        resp = self.do_request()
        self.save_into_file(resp.content)
        fetch_date = timezone.now()

        if self.is_file_untracked():
            commit_msg = 'New URL ({}) is now being tracked'.format(self.url_name)
            self.commit(commit_msg)
        elif self.is_file_different():
            commit_msg = 'Change detected on {} at {}'.format(self.url_name, fetch_date)
            utils.send_pushover(
                '{}: Change detected!'.format(self.project.project_name),
                commit_msg
            )
            self.commit(commit_msg)

        self.last_fetched_date = fetch_date

        if do_save:
            self.save()

        return resp

    def next_fetch(self):
        return self.last_fetched_date + self.fetch_frequency

    def get_commits(self):
        repo = self.project.get_repo()
        commits = repo.iter_commits('master')

        return list(filter(lambda x: self.get_full_filename() in x.stats.files, commits))

    def get_diff(self, commit_a, commit_b, u=16):
        commits = self.get_commits()
        assert u > 0
        assert commit_a in commits
        assert commit_b in commits

        repo = self.project.get_repo()
        return repo.git.diff(commit_a, commit_b, '-U{}'.format(u))

    def get_commit_from_sha(self, sha):
        commits = self.get_commits()

        for commit in commits:
            if commit.hexsha == sha:
                return commit

        return None


class Header(models.Model):
    url = models.ForeignKey(Url, on_delete=models.CASCADE)
    header_name = models.CharField('name', max_length=256)
    header_value = models.CharField('value', max_length=256)
    add_date = models.DateTimeField('date added', auto_now_add=True)

    def __str__(self):
        return self.header_name + ': ' + self.header_value
