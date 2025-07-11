# Generated by Django 5.2.1 on 2025-06-18 16:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_order_tx_ref_alter_order_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=100)),
                ('phone', models.CharField(max_length=20)),
                ('email', models.EmailField(max_length=254)),
                ('event_date', models.DateField()),
                ('product_type', models.CharField(choices=[('birthday_cake', 'Birthday Cake'), ('wedding_cake', 'Wedding Cake'), ('cupcakes', 'Cupcakes')], max_length=50)),
                ('servings', models.PositiveIntegerField()),
                ('flavor', models.CharField(max_length=100)),
                ('budget', models.CharField(choices=[('under_50', 'Under GHS 50'), ('50_to_100', 'GHS 50 - GHS 100'), ('over_100', 'Over GHS 100')], max_length=20)),
                ('requirements', models.TextField(blank=True)),
                ('design_description', models.TextField(blank=True)),
                ('additional_notes', models.TextField(blank=True)),
                ('delivery_option', models.CharField(choices=[('pickup', 'Pickup'), ('delivery', 'Delivery')], max_length=20)),
                ('delivery_address', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
