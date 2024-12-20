# Generated by Django 2.2.6 on 2019-11-10 00:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('council', '0003_auto_20191109_1729'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='agency',
            options={'ordering': ('agency_name', 'date_added'), 'verbose_name_plural': 'agencies'},
        ),
        migrations.AlterModelOptions(
            name='department',
            options={'ordering': ('agency', 'department_name')},
        ),
        migrations.AlterField(
            model_name='department',
            name='agency',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='departments', to='council.Agency'),
        ),
    ]
