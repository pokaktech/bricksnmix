# Generated by Django 3.2.14 on 2024-08-12 04:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0026_auto_20240724_0941'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cart',
            name='product',
        ),
        migrations.RemoveField(
            model_name='cart',
            name='quantity',
        ),
    ]
