# Generated by Django 5.1.3 on 2024-12-04 10:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prospects', '0004_alter_prospect_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='prospect',
            name='fields',
            field=models.JSONField(blank=True, default=dict),
        ),
    ]