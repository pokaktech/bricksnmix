# Generated by Django 3.2.14 on 2024-10-03 14:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0043_auto_20241001_0837'),
    ]

    operations = [
        migrations.AddField(
            model_name='deliveryaddress',
            name='is_default',
            field=models.BooleanField(default=False),
        ),
    ]