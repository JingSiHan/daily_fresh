# Generated by Django 2.2 on 2020-11-03 15:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goods',
            name='create_time',
            field=models.DateTimeField(auto_created=True, blank=True, verbose_name='创建时间'),
        ),
        migrations.AlterField(
            model_name='goodsimage',
            name='create_time',
            field=models.DateTimeField(auto_created=True, blank=True, verbose_name='创建时间'),
        ),
        migrations.AlterField(
            model_name='goodssku',
            name='create_time',
            field=models.DateTimeField(auto_created=True, blank=True, verbose_name='创建时间'),
        ),
        migrations.AlterField(
            model_name='goodstype',
            name='create_time',
            field=models.DateTimeField(auto_created=True, blank=True, verbose_name='创建时间'),
        ),
        migrations.AlterField(
            model_name='indexgoodsbanner',
            name='create_time',
            field=models.DateTimeField(auto_created=True, blank=True, verbose_name='创建时间'),
        ),
        migrations.AlterField(
            model_name='indexpromotionbanner',
            name='create_time',
            field=models.DateTimeField(auto_created=True, blank=True, verbose_name='创建时间'),
        ),
        migrations.AlterField(
            model_name='indextypegoodsbanner',
            name='create_time',
            field=models.DateTimeField(auto_created=True, blank=True, verbose_name='创建时间'),
        ),
    ]
