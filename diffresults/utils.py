from django.conf import settings

def create_gitdir(path):
    if path.exists():
        return False
    else:
        path.mkdir(parents=True)
        return True

