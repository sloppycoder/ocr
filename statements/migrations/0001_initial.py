# Generated by Django 5.0.4 on 2024-04-14 07:35

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Statement",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=64)),
                ("mime_type", models.CharField(max_length=32)),
                ("content", models.BinaryField()),
                ("content_sha", models.CharField(default="", max_length=40)),
                ("submitted_at", models.DateTimeField(auto_now_add=True)),
                ("owner", models.CharField(max_length=64)),
            ],
            options={
                "db_table": "statements",
            },
        ),
    ]
