# Generated by Django 2.2.6 on 2020-02-01 19:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0010_auto_20200201_1314'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='client_phone',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
