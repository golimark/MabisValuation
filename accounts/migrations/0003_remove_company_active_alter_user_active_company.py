# Generated by Django 5.1.3 on 2024-11-18 09:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_loancompany_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='company',
            name='active',
        ),
        migrations.AlterField(
            model_name='user',
            name='active_company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.loancompany'),
        ),
    ]
