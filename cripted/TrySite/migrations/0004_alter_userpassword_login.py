# Generated by Django 4.0.6 on 2022-07-22 18:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TrySite', '0003_alter_userpassword_login'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userpassword',
            name='login',
            field=models.CharField(max_length=255, verbose_name='login'),
        ),
    ]