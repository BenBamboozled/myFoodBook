# Generated by Django 3.1.3 on 2020-11-15 19:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foodBookApp', '0004_auto_20201115_1141'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='slug',
        ),
        migrations.RemoveField(
            model_name='post',
            name='tags',
        ),
    ]
