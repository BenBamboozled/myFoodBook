# Generated by Django 3.1.3 on 2020-11-15 20:14

from django.db import migrations, models
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0003_taggeditem_add_unique_index'),
        ('foodBookApp', '0007_post_tags'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='privacy',
            field=models.CharField(choices=[('public', 'Public'), ('private', 'Private'), ('friends', 'Friends Only')], default='Public', max_length=7),
        ),
        migrations.AlterField(
            model_name='post',
            name='body',
            field=models.TextField(max_length=300),
        ),
        migrations.AlterField(
            model_name='post',
            name='tags',
            field=taggit.managers.TaggableManager(blank=True, help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
    ]