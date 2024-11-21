# Generated by Django 5.1.3 on 2024-11-21 07:03

import django.db.models.deletion
import prospects.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CarType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='CarModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('model_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='models', to='prospects.cartype')),
            ],
        ),
        migrations.CreateModel(
            name='Prospect',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company', models.CharField(max_length=256)),
                ('name', models.CharField(max_length=255, verbose_name='NAME')),
                ('gender', models.CharField(choices=[('MALE', 'MALE'), ('FEMALE', 'FEMALE')], max_length=10, verbose_name='GENDER')),
                ('phone_number', models.CharField(max_length=10, validators=[prospects.models.validate_phone_number], verbose_name='PHONE NUMBER')),
                ('email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='EMAIL')),
                ('title', models.CharField(choices=[('MS.', 'MS.'), ('MR.', 'MR.')], verbose_name='TITLE')),
                ('alt_number', models.CharField(blank=True, max_length=10, null=True, validators=[prospects.models.validate_phone_number], verbose_name='OTHER PHONE NUMBER')),
                ('agent', models.CharField(max_length=256)),
                ('date_of_birth', models.DateField(blank=True, null=True, verbose_name='DATE OF BIRTH')),
                ('created_by', models.CharField(max_length=256)),
                ('decline_reason', models.CharField(blank=True, max_length=255, null=True)),
                ('proof_of_payment', models.CharField(blank=True, max_length=256, null=True)),
                ('proof_of_payment_id', models.CharField(blank=True, max_length=50, null=True, verbose_name='PROOF OF PAYMENT ID')),
                ('status', models.CharField(blank=True, choices=[('New', 'New'), ('Pending', 'Pending'), ('Valuation', 'Valuation'), ('Valuation Supervisor', 'Valuation Supervisor'), ('Payment Verified', 'Payment Verified'), ('Review', 'Review'), ('Pipeline', 'Pipeline'), ('Failed', 'Failed'), ('Declined', 'Declined')], default='New', max_length=20, null=True, verbose_name='STATUS')),
                ('slug', models.SlugField(blank=True, max_length=200, null=True, unique=True, verbose_name='Safe Url')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('asset_submitted_on', models.DateTimeField(blank=True, null=True)),
                ('asset_submitted_by', models.CharField(blank=True, max_length=256, null=True)),
                ('payment_verified_on', models.DateTimeField(blank=True, null=True)),
                ('payment_verified_by', models.CharField(blank=True, max_length=256, null=True)),
                ('submitted_for_valuation_on', models.DateTimeField(blank=True, null=True)),
                ('submitted_for_valuation_by', models.CharField(blank=True, max_length=256, null=True)),
                ('valuer_assigned_on', models.DateTimeField(blank=True, null=True)),
                ('valuer_assigned', models.CharField(blank=True, max_length=256, null=True)),
                ('valuation_submitted_on', models.DateTimeField(blank=True, null=True)),
                ('valuation_reviewd_on', models.DateTimeField(blank=True, null=True)),
                ('valuation_reviewd_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='valuation_reviewd_by', to=settings.AUTH_USER_MODEL)),
                ('valuation_submitted_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='valuation_submitted_by', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
