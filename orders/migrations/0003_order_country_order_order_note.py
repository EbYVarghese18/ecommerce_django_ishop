# Generated by Django 4.1.3 on 2022-12-09 11:04

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_remove_order_country_remove_order_order_note'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='country',
            field=models.CharField(default=django.utils.timezone.now, max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='order_note',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
