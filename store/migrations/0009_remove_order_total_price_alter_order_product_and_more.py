# Generated by Django 5.0.7 on 2024-08-28 07:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0008_order_status_order_total_price_alter_order_product"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="order",
            name="total_price",
        ),
        migrations.AlterField(
            model_name="order",
            name="product",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="store.product",
            ),
        ),
        migrations.AlterField(
            model_name="order",
            name="status",
            field=models.CharField(
                choices=[("pending", "Pending"), ("completed", "Completed")],
                default="pending",
                max_length=10,
            ),
        ),
    ]
