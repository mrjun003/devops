# Generated by Django 3.2.6 on 2021-10-27 10:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0006_alter_user_last_login_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='permission',
            name='desc',
            field=models.CharField(default='', max_length=200),
        ),
    ]
