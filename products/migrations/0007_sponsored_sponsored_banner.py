# Generated by Django 3.2.14 on 2024-12-23 10:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_sponsored_sponsoredproduct'),
    ]

    operations = [
        migrations.AddField(
            model_name='sponsored',
            name='sponsored_banner',
            field=models.ImageField(default=1, upload_to='sponsored_banners/'),
            preserve_default=False,
        ),
    ]