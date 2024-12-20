# Generated by Django 2.2.6 on 2020-04-04 18:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('council', '0035_auto_20200404_1331'),
    ]

    operations = [
        migrations.AlterField(
            model_name='highlight',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='highlights', to='council.Category'),
        ),
        migrations.AlterField(
            model_name='keyphrase',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='keyphrases', to='council.Category'),
        ),
        migrations.AlterField(
            model_name='keyphrase',
            name='phrase',
            field=models.CharField(max_length=200, verbose_name='keyphrase'),
        ),
    ]
