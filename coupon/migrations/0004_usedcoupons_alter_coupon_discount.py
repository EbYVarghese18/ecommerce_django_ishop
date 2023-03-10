# Generated by Django 4.1.2 on 2022-12-24 03:52

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coupon', '0003_rename_code_coupon_coupon_code_remove_coupon_active_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='UsedCoupons',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('coupon_code', models.CharField(max_length=50)),
                ('username', models.CharField(max_length=50)),
            ],
        ),
        migrations.AlterField(
            model_name='coupon',
            name='discount',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]
