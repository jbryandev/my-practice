# Generated by Django 2.2.6 on 2020-01-21 20:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('council', '0029_auto_20200119_0850'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='keyphrase',
            options={'ordering': ('kp_text', 'date_added')},
        ),
    ]
