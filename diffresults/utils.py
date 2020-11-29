from git import Repo
from django.conf import settings

import requests


def create_gitdir(path):
    if not path.exists():
        path.mkdir(parents=True)

    return Repo.init(path)


def send_pushover(title, message, attachment=None, **kwargs):
    assert settings.PUSHOVER_API_TOKEN is not None, 'You need to set the pushover token.'
    assert settings.PUSHOVER_API_USER is not None, 'You need to set the pushover user.'

    token = settings.PUSHOVER_API_TOKEN
    user = settings.PUSHOVER_API_USER
    url = 'https://api.pushover.net/1/messages.json'
    files = None

    post_data = {
        'token': token,
        'user': user,
        'message': message,
        'title': title,
    }

    if attachment is not None:
        assert type(attachment) is tuple, '''
        attachment must be of type tuple(). It should looke like so:

        ('image.EXT', file('file.EXT', 'rb'), 'MIME')
        '''
        files = {
            'attachment': attachment
        }

    resp = requests.post(url, data=dict(post_data, **kwargs), files=files)

    return resp
