# Generated by Django 3.2.14 on 2024-11-13 07:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0059_ratingreview_updated_at'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='product_rating',
        ),
        migrations.AddField(
            model_name='product',
            name='delivery_time',
            field=models.IntegerField(default=3),
        ),
        migrations.AlterField(
            model_name='ratingreview',
            name='product',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='accounts.product'),
        ),
    ]
