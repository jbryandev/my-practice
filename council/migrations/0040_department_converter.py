# Generated by Django 2.2.6 on 2020-04-12 02:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('council', '0039_converter'),
    ]

    operations = [
        migrations.AddField(
            model_name='department',
            name='converter',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='departments', to='council.Converter'),
            preserve_default=False,
        ),
    ]
