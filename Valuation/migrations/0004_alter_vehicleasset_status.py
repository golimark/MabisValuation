# Generated by Django 5.1.5 on 2025-03-12 12:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Valuation', '0003_alter_vehicleasset_maketypes_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vehicleasset',
            name='status',
            field=models.CharField(choices=[('Not valued', 'Not valued'), ('Valued', 'Valued'), ('Inspection required', 'Inspection required'), ('Inspected', 'Inspected'), ('In tracking', 'In tracking'), ('Unpossessed', 'Unpossessed'), ('Repossessed', 'Repossessed'), ('Impounded', 'Impounded'), ('Self parked', 'Self parked'), ('Reclaimed', 'Reclaimed'), ('Disposed off', 'Disposed off')], default='Not valued', verbose_name='Status'),
        ),
    ]
