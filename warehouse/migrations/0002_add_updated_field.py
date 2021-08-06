# Generated by Django 2.2.24 on 2021-08-06 15:06

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='producer',
            name='updated',
            field=models.DateTimeField(db_index=True, default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='product',
            name='updated',
            field=models.DateTimeField(db_index=True, default=django.utils.timezone.now),
        ),
    ]