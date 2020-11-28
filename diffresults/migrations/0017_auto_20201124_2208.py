# Generated by Django 3.1.2 on 2020-11-24 11:08

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diffresults', '0016_auto_20201124_2139'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='url',
            name='scheduled_task',
        ),
        migrations.AlterField(
            model_name='url',
            name='fetch_frequency',
            field=models.DurationField(choices=[(datetime.timedelta(seconds=300), 'Every five minutes'), (datetime.timedelta(seconds=21600), 'Six hours, every day'), (datetime.timedelta(seconds=1800), 'Every half hour'), (datetime.timedelta(days=1), 'Daily'), (datetime.timedelta(seconds=60), 'Every minute'), (datetime.timedelta(days=7), 'Weekly'), (datetime.timedelta(seconds=3600), 'Hourly')], default=datetime.timedelta(days=1), verbose_name='fetch frequency'),
        ),
        migrations.AlterField(
            model_name='url',
            name='file_ext',
            field=models.CharField(choices=[('js', 'js'), ('xml', 'xml'), ('txt', 'txt'), ('html', 'html')], default='txt', max_length=16, verbose_name='file extension'),
        ),
    ]
