# Generated by Django 3.1.2 on 2020-11-14 07:25

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diffresults', '0011_auto_20201107_0605'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='git_dir',
            field=models.FilePathField(default='temp', editable=False, path='/home/osboxes/Tools/WebHawk/webhawk/GitDir', verbose_name='git directory'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='url',
            name='fetch_frequency',
            field=models.DurationField(choices=[(datetime.timedelta(seconds=300), 'Every five minutes'), (datetime.timedelta(seconds=60), 'Every minute'), (datetime.timedelta(seconds=21600), 'Six hours, every day'), (datetime.timedelta(days=7), 'Weekly'), (datetime.timedelta(days=1), 'Daily'), (datetime.timedelta(seconds=1800), 'Every half hour'), (datetime.timedelta(seconds=3600), 'Hourly')], default=datetime.timedelta(days=1), verbose_name='fetch frequency'),
        ),
        migrations.AlterField(
            model_name='url',
            name='file_ext',
            field=models.CharField(choices=[('xml', 'xml'), ('js', 'js'), ('html', 'html')], default='txt', max_length=16, verbose_name='file extension'),
        ),
    ]
