<<<<<<< HEAD
# Generated by Django 3.1.3 on 2020-11-24 01:11
=======
# Generated by Django 3.1.3 on 2020-11-24 00:33
>>>>>>> user_update

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foodBookApp', '0026_merge_20201123_1321'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='total_comments',
        ),
    ]
