# Generated by Django 2.2.6 on 2020-02-03 05:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0014_writeup'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='project_writeup',
        ),
    ]
