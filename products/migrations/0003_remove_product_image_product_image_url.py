# Generated by Django 5.2.3 on 2025-06-14 22:21

import products.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_product_is_featured'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='image',
        ),
        migrations.AddField(
            model_name='product',
            name='image_url',
            field=models.URLField(blank=True, help_text='Paste an image URL (e.g., from a website)', max_length=500, null=True, validators=[products.models.validate_image_url]),
        ),
    ]
