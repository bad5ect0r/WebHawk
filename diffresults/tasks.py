from diffresults.models import Url


def fetch_url(url_id):
    url = Url.objects.get(pk=url_id)
    url.fetch()
