# Generated by Django 2.2 on 2020-11-03 15:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0002_auto_20201103_1834'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ordergoods',
            name='create_time',
            field=models.DateTimeField(auto_created=True, blank=True, verbose_name='创建时间'),
        ),
        migrations.AlterField(
            model_name='orderinfo',
            name='create_time',
            field=models.DateTimeField(auto_created=True, blank=True, verbose_name='创建时间'),
        ),
    ]
