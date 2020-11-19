# Generated by Django 3.1.3 on 2020-11-16 00:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodBookApp', '0010_auto_20201115_1748'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='friends',
        ),
        migrations.AlterField(
            model_name='profile',
            name='profilePic',
            field=models.ImageField(default='default.jpg', upload_to='profile_pics'),
        ),
    ]