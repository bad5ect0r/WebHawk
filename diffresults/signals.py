from django.db.models.signals import post_save
from django.dispatch import receiver

from diffresults.models import Url

from django_q.tasks import Schedule


@receiver(post_save, sender=Url)
def fetch_saved_url(sender, instance, created, **kwargs):
    if created:
        instance.fetch()


@receiver(post_save, sender=Url)
def create_scheduled_task(sender, instance, created, **kwargs):
    if created:
        schedule_type = Schedule.DAILY
        minutes = 0

        if instance.fetch_frequency == Url.ONE_MINUTE:
            minutes = 1
            schedule_type = Schedule.MINUTES
        elif instance.fetch_frequency == Url.WEEKLY:
            schedule_type = Schedule.WEEKLY
        elif instance.fetch_frequency == Url.SIX_HOURS:
            minutes = 360
            schedule_type = Schedule.MINUTES
        elif instance.fetch_frequency == Url.HOURLY:
            minutes = 60
            schedule_type = Schedule.MINUTES
        elif instance.fetch_frequency == Url.HALF_HOURLY:
            minutes = 30
            schedule_type = Schedule.MINUTES
        elif instance.fetch_frequency == Url.FIVE_MINUTES:
            minutes = 5
            schedule_type = Schedule.MINUTES

        Schedule.objects.create(
            url=instance,
            func='diffresults.tasks.fetch_url',
            args=str(instance.id),
            schedule_type=schedule_type,
            minutes=minutes,
            next_run=instance.next_fetch()
        )
