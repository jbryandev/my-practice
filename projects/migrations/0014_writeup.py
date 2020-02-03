# Generated by Django 2.2.6 on 2020-02-03 05:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0013_auto_20200201_1911'),
    ]

    operations = [
        migrations.CreateModel(
            name='Writeup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('focus', models.CharField(max_length=200)),
                ('project_writeup', models.TextField(blank=True, null=True)),
                ('date_added', models.DateTimeField(blank=True, null=True)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='writeups', to='projects.Project')),
            ],
        ),
    ]
