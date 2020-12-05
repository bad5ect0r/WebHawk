from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from diffresults.models import Url

from django_q.tasks import Schedule


@receiver(pre_save, sender=Url)
def fetch_saved_url(sender, instance, **kwargs):
    if instance._state.adding:
        instance.fetch(do_save=False)


@receiver(post_save, sender=Url)
def create_scheduled_task(sender, instance, created, **kwargs):
    if created:
        Schedule.objects.create(
            url=instance,
            func='diffresults.tasks.fetch_url',
            args=str(instance.id),
            schedule_type=Schedule.MINUTES,
            minutes=int(instance.fetch_frequency.total_seconds() / 60),
            next_run=instance.next_fetch()
        )
    else:
        instance.schedule.minutes = int(instance.fetch_frequency.total_seconds() / 60)
        instance.schedule.next_run = instance.next_fetch()
        instance.schedule.save()
