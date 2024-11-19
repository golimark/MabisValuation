# Generated by Django 5.1.3 on 2024-11-19 06:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_remove_company_active_alter_user_active_company'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='companies',
        ),
        migrations.AddField(
            model_name='user',
            name='company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='company', to='accounts.company'),
        ),
    ]