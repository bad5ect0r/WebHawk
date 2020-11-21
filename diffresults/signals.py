from django.db.models.signals import post_save
from django.dispatch import receiver

from diffresults.models import Url


@receiver(post_save, sender=Url)
def fetch_saved_url(sender, instance, created, **kwargs):
    if created:
        instance.fetch()
