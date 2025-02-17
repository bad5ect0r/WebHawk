# Generated by Django 3.1.2 on 2020-10-11 05:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Domain',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_domain_name', models.CharField(max_length=253)),
                ('add_date', models.DateTimeField(verbose_name='date added')),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project_name', models.CharField(max_length=256)),
                ('create_date', models.DateTimeField(verbose_name='date created')),
            ],
        ),
        migrations.CreateModel(
            name='Url',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_url', models.CharField(max_length=2048)),
                ('domain', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='diffresults.domain')),
            ],
        ),
        migrations.AddField(
            model_name='domain',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='diffresults.project'),
        ),
    ]
