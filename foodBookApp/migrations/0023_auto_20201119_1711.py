# Generated by Django 3.1.3 on 2020-11-19 23:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodBookApp', '0022_comment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='body',
            field=models.CharField(max_length=100),
        ),
    ]
