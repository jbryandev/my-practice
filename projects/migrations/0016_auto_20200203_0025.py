# Generated by Django 2.2.6 on 2020-02-03 06:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0015_remove_project_project_writeup'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='writeup',
            options={'ordering': ('pk', '-date_added')},
        ),
        migrations.AlterField(
            model_name='project',
            name='client_name',
            field=models.CharField(max_length=200, verbose_name='client'),
        ),
    ]
