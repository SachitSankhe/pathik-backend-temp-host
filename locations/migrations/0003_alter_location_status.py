# Generated by Django 4.1.1 on 2022-12-24 13:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("locations", "0002_alter_location_address_alter_location_description"),
    ]

    operations = [
        migrations.AlterField(
            model_name="location",
            name="status",
            field=models.BooleanField(default=False),
        ),
    ]