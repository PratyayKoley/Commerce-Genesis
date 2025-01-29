# Generated by Django 5.1.5 on 2025-01-29 05:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainApp', '0002_product_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='category',
            field=models.CharField(choices=[('Electronics', 'Electronics'), ('Gaming', 'Gaming'), ('Accessories', 'Accessories'), ('Furniture', 'Furniture'), ('Wearable', 'Wearable'), ('Other', 'Other')], default='Other', max_length=50),
        ),
    ]
