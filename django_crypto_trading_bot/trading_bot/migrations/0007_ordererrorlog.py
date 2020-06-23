# Generated by Django 3.0.5 on 2020-06-19 15:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("trading_bot", "0006_auto_20200619_1150"),
    ]

    operations = [
        migrations.CreateModel(
            name="OrderErrorLog",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                (
                    "error_type",
                    models.CharField(
                        choices=[("Insufficient Funds", "Insufficient Funds")],
                        max_length=50,
                    ),
                ),
                ("error_message", models.TextField(blank=True, null=True)),
                (
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="error_log",
                        to="trading_bot.Order",
                    ),
                ),
            ],
        ),
    ]