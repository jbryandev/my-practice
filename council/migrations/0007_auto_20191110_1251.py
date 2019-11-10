# Generated by Django 2.2.6 on 2019-11-10 18:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('council', '0006_auto_20191109_2114'),
    ]

    operations = [
        migrations.AddField(
            model_name='agenda',
            name='pdf_link',
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='department',
            name='meeting_info',
            field=models.TextField(blank=True, null=True),
        ),
    ]
