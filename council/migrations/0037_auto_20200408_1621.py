# Generated by Django 2.2.6 on 2020-04-08 21:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('council', '0036_auto_20200404_1348'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='highlight',
            options={'ordering': ('agenda__agency', 'agenda__department', 'agenda', 'date_added')},
        ),
        migrations.AlterModelOptions(
            name='keyphrase',
            options={'ordering': ('category', 'phrase', 'date_added')},
        ),
    ]
