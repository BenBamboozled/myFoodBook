# Generated by Django 3.1.3 on 2020-11-27 02:17

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('foodBookApp', '0027_remove_post_total_comments'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='likes',
            field=models.ManyToManyField(blank=True, related_name='like_post', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='post',
            name='privacy',
            field=models.CharField(choices=[('public', 'Public'), ('private', 'Private'), ('friends', 'Friends Only')], default='public', max_length=7),
        ),
        migrations.AlterField(
            model_name='profile',
            name='privacy',
            field=models.CharField(choices=[('public', 'Public'), ('private', 'Private'), ('friends', 'Friends Only')], default='public', max_length=7),
        ),
    ]
