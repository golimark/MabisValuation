# Generated by Django 5.1.5 on 2025-02-06 07:53

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Valuation', '0001_initial'),
        ('prospects', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='landasset',
            name='prospect',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='prospects.prospect'),
        ),
        migrations.AddField(
            model_name='landevaluationreport',
            name='land',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Valuation.landasset'),
        ),
        migrations.AddField(
            model_name='landevaluationreport',
            name='prospect',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='prospects.prospect'),
        ),
        migrations.AddField(
            model_name='vehicleasset',
            name='prospect',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='prospects.prospect'),
        ),
        migrations.AddField(
            model_name='vehicleevaluationreport',
            name='company_approver',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='company_approver', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='vehicleevaluationreport',
            name='company_supervisor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='company_supervisor', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='vehicleevaluationreport',
            name='company_valuer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='company_valuer', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='vehicleevaluationreport',
            name='prospect',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='prospects.prospect'),
        ),
        migrations.AddField(
            model_name='vehicleevaluationreport',
            name='vehicle',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Valuation.vehicleasset'),
        ),
        migrations.AddField(
            model_name='vehicleinspectionreport',
            name='prospect',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='prospects.prospect'),
        ),
        migrations.AddField(
            model_name='vehicleinspectionreport',
            name='vehicle',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Valuation.vehicleasset'),
        ),
    ]
