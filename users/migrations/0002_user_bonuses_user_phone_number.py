# Generated by Django 4.2.13 on 2024-05-28 18:59

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="bonuses",
            field=models.DecimalField(
                decimal_places=2, default=50, max_digits=7, verbose_name="Бонусы"
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="phone_number",
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
