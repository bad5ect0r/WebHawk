from django.conf import settings

from git import Repo


def create_gitdir(path):
    if not path.exists():
        path.mkdir(parents=True)

    return Repo.init(path)

