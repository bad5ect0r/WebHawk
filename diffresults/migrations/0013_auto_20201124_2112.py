# Generated by Django 3.1.2 on 2020-11-24 10:12

import datetime
import diffresults.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('django_q', '0013_task_attempt_count'),
        ('diffresults', '0012_auto_20201114_0725'),
    ]

    operations = [
        migrations.AddField(
            model_name='url',
            name='scheduled_task',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='django_q.schedule'),
        ),
        migrations.AlterField(
            model_name='url',
            name='add_date',
            field=models.DateTimeField(auto_now_add=True, validators=[diffresults.validators.date_in_past], verbose_name='date added'),
        ),
        migrations.AlterField(
            model_name='url',
            name='fetch_frequency',
            field=models.DurationField(choices=[(datetime.timedelta(seconds=3600), 'Hourly'), (datetime.timedelta(seconds=1800), 'Every half hour'), (datetime.timedelta(seconds=21600), 'Six hours, every day'), (datetime.timedelta(seconds=300), 'Every five minutes'), (datetime.timedelta(seconds=60), 'Every minute'), (datetime.timedelta(days=1), 'Daily'), (datetime.timedelta(days=7), 'Weekly')], default=datetime.timedelta(days=1), verbose_name='fetch frequency'),
        ),
        migrations.AlterField(
            model_name='url',
            name='file_ext',
            field=models.CharField(choices=[('js', 'js'), ('html', 'html'), ('xml', 'xml'), ('txt', 'txt')], default='txt', max_length=16, verbose_name='file extension'),
        ),
        migrations.AlterField(
            model_name='url',
            name='last_fetched_date',
            field=models.DateTimeField(editable=False, null=True, validators=[diffresults.validators.date_in_past], verbose_name='date last fetched'),
        ),
    ]
