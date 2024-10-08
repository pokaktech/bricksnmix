# Generated by Django 3.2.25 on 2024-08-12 07:58

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounts', '0027_deliveryaddress_order_orderitem_productimage'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Order',
            new_name='CustomerOrder',
        ),
        migrations.RemoveField(
            model_name='orderitem',
            name='actual_price',
        ),
        migrations.RemoveField(
            model_name='orderitem',
            name='offer_percent',
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='quantity',
            field=models.IntegerField(),
        ),
    ]
