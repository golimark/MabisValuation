# Generated by Django 5.1.3 on 2025-01-23 10:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Valuation', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vehicleasset',
            name='maketypes',
            field=models.CharField(blank=True, choices=[('ACURA', 'ACURA'), ('ALFA_ROMEO', 'ALFA ROMEO'), ('AUDI', 'AUDI'), ('BMW', 'BMW'), ('BUICK', 'BUICK'), ('CADILLAC', 'CADILLAC'), ('CHEVROLET', 'CHEVROLET'), ('CHRYSLER', 'CHRYSLER'), ('CITROEN', 'CITROËN'), ('DODGE', 'DODGE'), ('FERRARI', 'FERRARI'), ('FIAT', 'FIAT'), ('FORD', 'FORD'), ('GMC', 'GMC'), ('HONDA', 'HONDA'), ('HYUNDAI', 'HYUNDAI'), ('JAGUAR', 'JAGUAR'), ('JEEP', 'JEEP'), ('KIA', 'KIA'), ('LAND_ROVER', 'LAND ROVER'), ('LEXUS', 'LEXUS'), ('LINCOLN', 'LINCOLN'), ('MASERATI', 'MASERATI'), ('MAZDA', 'MAZDA'), ('MCLAREN', 'MCLAREN'), ('MERCEDES_BENZ', 'MERCEDES-BENZ'), ('MITSUBISHI', 'MITSUBISHI'), ('NISSAN', 'NISSAN'), ('PAGANI', 'PAGANI'), ('PEUGEOT', 'PEUGEOT'), ('PORSCHE', 'PORSCHE'), ('RAM', 'RAM'), ('RENAULT', 'RENAULT'), ('ROLLS_ROYCE', 'ROLLS-ROYCE'), ('SAAB', 'SAAB'), ('SUBARU', 'SUBARU'), ('SUZUKI', 'SUZUKI'), ('TESLA', 'TESLA'), ('TOYOTA', 'TOYOTA'), ('VOLKSWAGEN', 'VOLKSWAGEN'), ('VOLVO', 'VOLVO'), ('OTHER', 'OTHER')], max_length=50, null=True, verbose_name='Car Make Type'),
        ),
        migrations.AlterField(
            model_name='vehicleevaluationreport',
            name='body_description',
            field=models.CharField(choices=[('SALOON', 'SALOON'), ('SUV', 'SUV'), ('STATION WAGON', 'STATION WAGON'), ('MINI-VAN', 'MINI-VAN'), ('SEDAN', 'SEDAN'), ('COUPE', 'COUPE'), ('PICK UP DOUBLE CABIN', 'PICK UP DOUBLE CABIN'), ('PICK UP SINGLE CABIN', 'PICK UP SINGLE CABIN')], max_length=200, null=True, verbose_name='body description'),
        ),
        migrations.AlterField(
            model_name='vehicleevaluationreport',
            name='maketypes',
            field=models.CharField(blank=True, choices=[('ACURA', 'ACURA'), ('ALFA_ROMEO', 'ALFA ROMEO'), ('AUDI', 'AUDI'), ('BMW', 'BMW'), ('BUICK', 'BUICK'), ('CADILLAC', 'CADILLAC'), ('CHEVROLET', 'CHEVROLET'), ('CHRYSLER', 'CHRYSLER'), ('CITROEN', 'CITROËN'), ('DODGE', 'DODGE'), ('FERRARI', 'FERRARI'), ('FIAT', 'FIAT'), ('FORD', 'FORD'), ('GMC', 'GMC'), ('HONDA', 'HONDA'), ('HYUNDAI', 'HYUNDAI'), ('JAGUAR', 'JAGUAR'), ('JEEP', 'JEEP'), ('KIA', 'KIA'), ('LAND_ROVER', 'LAND ROVER'), ('LEXUS', 'LEXUS'), ('LINCOLN', 'LINCOLN'), ('MASERATI', 'MASERATI'), ('MAZDA', 'MAZDA'), ('MCLAREN', 'MCLAREN'), ('MERCEDES_BENZ', 'MERCEDES-BENZ'), ('MITSUBISHI', 'MITSUBISHI'), ('NISSAN', 'NISSAN'), ('PAGANI', 'PAGANI'), ('PEUGEOT', 'PEUGEOT'), ('PORSCHE', 'PORSCHE'), ('RAM', 'RAM'), ('RENAULT', 'RENAULT'), ('ROLLS_ROYCE', 'ROLLS-ROYCE'), ('SAAB', 'SAAB'), ('SUBARU', 'SUBARU'), ('SUZUKI', 'SUZUKI'), ('TESLA', 'TESLA'), ('TOYOTA', 'TOYOTA'), ('VOLKSWAGEN', 'VOLKSWAGEN'), ('VOLVO', 'VOLVO'), ('OTHER', 'OTHER')], max_length=50, null=True, verbose_name='Car Make Type'),
        ),
        migrations.AlterField(
            model_name='vehicleevaluationreport',
            name='year_of_manufacture',
            field=models.IntegerField(choices=[(1997, 1997), (1998, 1998), (1999, 1999), (2000, 2000), (2001, 2001), (2002, 2002), (2003, 2003), (2004, 2004), (2005, 2005), (2006, 2006), (2007, 2007), (2008, 2008), (2009, 2009), (2010, 2010), (2011, 2011), (2012, 2012), (2013, 2013), (2014, 2014), (2015, 2015), (2016, 2016), (2017, 2017), (2018, 2018), (2019, 2019), (2020, 2020), (2021, 2021), (2022, 2022), (2023, 2023), (2024, 2024)], null=True, verbose_name='Year of manufacture'),
        ),
    ]
