# Generated by Django 4.1.2 on 2022-12-24 03:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coupon', '0004_usedcoupons_alter_coupon_discount'),
    ]

    operations = [
        migrations.RenameField(
            model_name='usedcoupons',
            old_name='username',
            new_name='email',
        ),
    ]