# Generated by Django 3.2.14 on 2024-12-07 08:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_notification_heading'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='status',
            field=models.CharField(choices=[('0', 'Pending'), ('1', 'Ordered'), ('2', 'Shipped'), ('3', 'Delivered'), ('4', 'Cancelled')], default='1', max_length=50),
        ),
    ]
