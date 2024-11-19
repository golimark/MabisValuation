# Generated by Django 5.1.3 on 2024-11-15 16:30

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LandAsset',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('land_location', models.CharField(verbose_name='LAND LOCATION')),
                ('landtitle', models.FileField(blank=True, null=True, upload_to='prospect/landtitle/')),
                ('slug', models.SlugField(blank=True, max_length=200, null=True, unique=True, verbose_name='Safe Url')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='LandEvaluationReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(blank=True, max_length=200, null=True, unique=True, verbose_name='Safe Url')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='VehicleAsset',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('logbook', models.CharField(blank=True, max_length=256, null=True)),
                ('license_plate', models.CharField(max_length=20, verbose_name='Vehicle Registration Number')),
                ('maketypes', models.CharField(blank=True, choices=[('NISSAN', 'NISSAN'), ('TOYOTA', 'TOYOTA'), ('OTHER', 'OTHER')], max_length=50, null=True, verbose_name='Car Make Type')),
                ('make', models.CharField(blank=True, max_length=50, null=True, verbose_name='Car Make')),
                ('model', models.CharField(blank=True, max_length=50, null=True, verbose_name='Car Model')),
                ('location', models.CharField(max_length=255, verbose_name='location of vehicle')),
                ('status', models.CharField(choices=[('NOT VALUED', 'NOT VALUED'), ('VALUED', 'VALUED'), ('IN TRACKING', 'IN TRACKING'), ('UNPOCESSED', 'UNPOCESSED'), ('REPOSESSED', 'REPOSESSED'), ('IMPOUNDED', 'IMPOUNDED'), ('SELF_PARKED', 'SELF_PARKED'), ('RECLAIMED', 'RECLAIMED'), ('DISPOSED_OFF', 'DISPOSED_OFF')], default='NOT VALUED', verbose_name='Status')),
                ('slug', models.SlugField(blank=True, max_length=200, null=True, unique=True, verbose_name='Safe Url')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='VehicleEvaluationReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_in_logbook', models.CharField(default=None, max_length=100)),
                ('tax_identification_number', models.CharField(max_length=50)),
                ('date_of_registration', models.DateField(null=True, verbose_name='date of registration')),
                ('make', models.CharField(blank=True, max_length=50, null=True, verbose_name='Car Make')),
                ('model', models.CharField(blank=True, max_length=50, null=True, verbose_name='Car Model')),
                ('body_description', models.CharField(choices=[('SALOON', 'SALOON'), ('SUV', 'SUV'), ('STATION WAGON', 'STATION WAGON'), ('MINI-VAN', 'MINI-VAN'), ('SEDAN', 'SEDAN'), ('COUPE', 'COUPE')], max_length=200, null=True, verbose_name='body description')),
                ('color_by_logbook', models.CharField(max_length=30, null=True, verbose_name='colour as per logbook')),
                ('fuel_type', models.CharField(blank=True, choices=[('DIESEL', 'DIESEL'), ('PETROL', 'PETROL'), ('ELECTRIC', 'ELECTRIC')], max_length=10, null=True, verbose_name='Fuel Type')),
                ('mileage', models.IntegerField(null=True, verbose_name='milage')),
                ('power', models.IntegerField(blank=True, null=True, verbose_name='Power(cubic capacity)')),
                ('gearbox_transmission', models.CharField(choices=[('AUTOMATIC', 'AUTOMATIC'), ('MANUAL', 'MANUAL'), ('HYBRID', 'HYBRID'), ('ELECTRIC', 'ELECTRIC')], max_length=50, null=True, verbose_name='Gear box transmission')),
                ('engine_number', models.CharField(max_length=50, null=True, verbose_name='engine number')),
                ('chassis_number', models.CharField(max_length=50, null=True, verbose_name='chassis number')),
                ('country_of_origin', models.CharField(max_length=50, null=True, verbose_name='Country of origin')),
                ('year_of_manufacture', models.IntegerField(choices=[(1998, 1998), (1999, 1999), (2000, 2000), (2001, 2001), (2002, 2002), (2003, 2003), (2004, 2004), (2005, 2005), (2006, 2006), (2007, 2007), (2008, 2008), (2009, 2009), (2010, 2010), (2011, 2011), (2012, 2012), (2013, 2013), (2014, 2014), (2015, 2015), (2016, 2016), (2017, 2017), (2018, 2018), (2019, 2019), (2020, 2020), (2021, 2021), (2022, 2022)], null=True, verbose_name='Year of manufacture')),
                ('years_since_on_uganda_roads', models.IntegerField(null=True, verbose_name='years since on uganda roads')),
                ('seating_capacity', models.IntegerField(blank=True, default=0, null=True)),
                ('place_of_inspection', models.CharField(max_length=100)),
                ('date_of_valuation', models.DateTimeField()),
                ('valuation_report_date', models.DateField()),
                ('color_by_inspection', models.CharField(blank=True, max_length=30, null=True, verbose_name='colour as per inspection')),
                ('chassis_frame', models.CharField(choices=[('IN VERY BAD SHAPE', 'IN VERY BAD SHAPE'), ('IN BAD SHAPE', 'IN BAD SHAPE'), ('IN GOOD SHAPE', 'IN GOOD SHAPE'), ('IN VERY GOOD SHAPE', 'IN VERY GOOD SHAPE'), ('IN EXCELLENT SHAPE', 'IN EXCELLENT SHAPE'), ('IN PERFECT SHAPE', 'IN PERFECT SHAPE'), ('IN NEW CONDITION', 'IN NEW CONDITION'), ('IN SHOWROOM CONDITION', 'IN SHOWROOM CONDITION')], max_length=100)),
                ('body_shell_paint', models.CharField(choices=[('IN VERY BAD SHAPE', 'IN VERY BAD SHAPE'), ('IN BAD SHAPE', 'IN BAD SHAPE'), ('IN GOOD SHAPE', 'IN GOOD SHAPE'), ('IN VERY GOOD SHAPE', 'IN VERY GOOD SHAPE'), ('IN EXCELLENT SHAPE', 'IN EXCELLENT SHAPE'), ('IN PERFECT SHAPE', 'IN PERFECT SHAPE'), ('IN NEW CONDITION', 'IN NEW CONDITION'), ('IN SHOWROOM CONDITION', 'IN SHOWROOM CONDITION')], max_length=100)),
                ('condition_of_seats', models.CharField(choices=[('IN VERY BAD SHAPE', 'IN VERY BAD SHAPE'), ('IN BAD SHAPE', 'IN BAD SHAPE'), ('IN GOOD SHAPE', 'IN GOOD SHAPE'), ('IN VERY GOOD SHAPE', 'IN VERY GOOD SHAPE'), ('IN EXCELLENT SHAPE', 'IN EXCELLENT SHAPE'), ('IN PERFECT SHAPE', 'IN PERFECT SHAPE'), ('IN NEW CONDITION', 'IN NEW CONDITION'), ('IN SHOWROOM CONDITION', 'IN SHOWROOM CONDITION')])),
                ('engine_assembly', models.CharField(choices=[('IN VERY BAD SHAPE', 'IN VERY BAD SHAPE'), ('IN BAD SHAPE', 'IN BAD SHAPE'), ('IN GOOD SHAPE', 'IN GOOD SHAPE'), ('IN VERY GOOD SHAPE', 'IN VERY GOOD SHAPE'), ('IN EXCELLENT SHAPE', 'IN EXCELLENT SHAPE'), ('IN PERFECT SHAPE', 'IN PERFECT SHAPE'), ('IN NEW CONDITION', 'IN NEW CONDITION'), ('IN SHOWROOM CONDITION', 'IN SHOWROOM CONDITION')])),
                ('accessories', models.CharField(choices=[('IN VERY BAD SHAPE', 'IN VERY BAD SHAPE'), ('IN BAD SHAPE', 'IN BAD SHAPE'), ('IN GOOD SHAPE', 'IN GOOD SHAPE'), ('IN VERY GOOD SHAPE', 'IN VERY GOOD SHAPE'), ('IN EXCELLENT SHAPE', 'IN EXCELLENT SHAPE'), ('IN PERFECT SHAPE', 'IN PERFECT SHAPE'), ('IN NEW CONDITION', 'IN NEW CONDITION'), ('IN SHOWROOM CONDITION', 'IN SHOWROOM CONDITION')], max_length=100)),
                ('cooling_system', models.CharField(choices=[('IN VERY BAD SHAPE', 'IN VERY BAD SHAPE'), ('IN BAD SHAPE', 'IN BAD SHAPE'), ('IN GOOD SHAPE', 'IN GOOD SHAPE'), ('IN VERY GOOD SHAPE', 'IN VERY GOOD SHAPE'), ('IN EXCELLENT SHAPE', 'IN EXCELLENT SHAPE'), ('IN PERFECT SHAPE', 'IN PERFECT SHAPE'), ('IN NEW CONDITION', 'IN NEW CONDITION'), ('IN SHOWROOM CONDITION', 'IN SHOWROOM CONDITION')])),
                ('gearbox_assembly', models.CharField(choices=[('IN VERY BAD SHAPE', 'IN VERY BAD SHAPE'), ('IN BAD SHAPE', 'IN BAD SHAPE'), ('IN GOOD SHAPE', 'IN GOOD SHAPE'), ('IN VERY GOOD SHAPE', 'IN VERY GOOD SHAPE'), ('IN EXCELLENT SHAPE', 'IN EXCELLENT SHAPE'), ('IN PERFECT SHAPE', 'IN PERFECT SHAPE'), ('IN NEW CONDITION', 'IN NEW CONDITION'), ('IN SHOWROOM CONDITION', 'IN SHOWROOM CONDITION')])),
                ('transmission_system', models.CharField(choices=[('IN VERY BAD SHAPE', 'IN VERY BAD SHAPE'), ('IN BAD SHAPE', 'IN BAD SHAPE'), ('IN GOOD SHAPE', 'IN GOOD SHAPE'), ('IN VERY GOOD SHAPE', 'IN VERY GOOD SHAPE'), ('IN EXCELLENT SHAPE', 'IN EXCELLENT SHAPE'), ('IN PERFECT SHAPE', 'IN PERFECT SHAPE'), ('IN NEW CONDITION', 'IN NEW CONDITION'), ('IN SHOWROOM CONDITION', 'IN SHOWROOM CONDITION')])),
                ('steering_system', models.CharField(choices=[('IN VERY BAD SHAPE', 'IN VERY BAD SHAPE'), ('IN BAD SHAPE', 'IN BAD SHAPE'), ('IN GOOD SHAPE', 'IN GOOD SHAPE'), ('IN VERY GOOD SHAPE', 'IN VERY GOOD SHAPE'), ('IN EXCELLENT SHAPE', 'IN EXCELLENT SHAPE'), ('IN PERFECT SHAPE', 'IN PERFECT SHAPE'), ('IN NEW CONDITION', 'IN NEW CONDITION'), ('IN SHOWROOM CONDITION', 'IN SHOWROOM CONDITION')])),
                ('suspension', models.CharField(choices=[('IN VERY BAD SHAPE', 'IN VERY BAD SHAPE'), ('IN BAD SHAPE', 'IN BAD SHAPE'), ('IN GOOD SHAPE', 'IN GOOD SHAPE'), ('IN VERY GOOD SHAPE', 'IN VERY GOOD SHAPE'), ('IN EXCELLENT SHAPE', 'IN EXCELLENT SHAPE'), ('IN PERFECT SHAPE', 'IN PERFECT SHAPE'), ('IN NEW CONDITION', 'IN NEW CONDITION'), ('IN SHOWROOM CONDITION', 'IN SHOWROOM CONDITION')])),
                ('braking_system', models.CharField(choices=[('IN VERY BAD SHAPE', 'IN VERY BAD SHAPE'), ('IN BAD SHAPE', 'IN BAD SHAPE'), ('IN GOOD SHAPE', 'IN GOOD SHAPE'), ('IN VERY GOOD SHAPE', 'IN VERY GOOD SHAPE'), ('IN EXCELLENT SHAPE', 'IN EXCELLENT SHAPE'), ('IN PERFECT SHAPE', 'IN PERFECT SHAPE'), ('IN NEW CONDITION', 'IN NEW CONDITION'), ('IN SHOWROOM CONDITION', 'IN SHOWROOM CONDITION')])),
                ('electrical_system', models.CharField(choices=[('IN VERY BAD SHAPE', 'IN VERY BAD SHAPE'), ('IN BAD SHAPE', 'IN BAD SHAPE'), ('IN GOOD SHAPE', 'IN GOOD SHAPE'), ('IN VERY GOOD SHAPE', 'IN VERY GOOD SHAPE'), ('IN EXCELLENT SHAPE', 'IN EXCELLENT SHAPE'), ('IN PERFECT SHAPE', 'IN PERFECT SHAPE'), ('IN NEW CONDITION', 'IN NEW CONDITION'), ('IN SHOWROOM CONDITION', 'IN SHOWROOM CONDITION')])),
                ('windshield', models.CharField(choices=[('IN VERY BAD SHAPE', 'IN VERY BAD SHAPE'), ('IN BAD SHAPE', 'IN BAD SHAPE'), ('IN GOOD SHAPE', 'IN GOOD SHAPE'), ('IN VERY GOOD SHAPE', 'IN VERY GOOD SHAPE'), ('IN EXCELLENT SHAPE', 'IN EXCELLENT SHAPE'), ('IN PERFECT SHAPE', 'IN PERFECT SHAPE'), ('IN NEW CONDITION', 'IN NEW CONDITION'), ('IN SHOWROOM CONDITION', 'IN SHOWROOM CONDITION')])),
                ('air_conditioning_system', models.CharField(choices=[('IN VERY BAD SHAPE', 'IN VERY BAD SHAPE'), ('IN BAD SHAPE', 'IN BAD SHAPE'), ('IN GOOD SHAPE', 'IN GOOD SHAPE'), ('IN VERY GOOD SHAPE', 'IN VERY GOOD SHAPE'), ('IN EXCELLENT SHAPE', 'IN EXCELLENT SHAPE'), ('IN PERFECT SHAPE', 'IN PERFECT SHAPE'), ('IN NEW CONDITION', 'IN NEW CONDITION'), ('IN SHOWROOM CONDITION', 'IN SHOWROOM CONDITION')])),
                ('wheels', models.CharField(choices=[('IN VERY BAD SHAPE', 'IN VERY BAD SHAPE'), ('IN BAD SHAPE', 'IN BAD SHAPE'), ('IN GOOD SHAPE', 'IN GOOD SHAPE'), ('IN VERY GOOD SHAPE', 'IN VERY GOOD SHAPE'), ('IN EXCELLENT SHAPE', 'IN EXCELLENT SHAPE'), ('IN PERFECT SHAPE', 'IN PERFECT SHAPE'), ('IN NEW CONDITION', 'IN NEW CONDITION'), ('IN SHOWROOM CONDITION', 'IN SHOWROOM CONDITION')])),
                ('tyre_condition', models.CharField(choices=[('IN VERY BAD SHAPE', 'IN VERY BAD SHAPE'), ('IN BAD SHAPE', 'IN BAD SHAPE'), ('IN GOOD SHAPE', 'IN GOOD SHAPE'), ('IN VERY GOOD SHAPE', 'IN VERY GOOD SHAPE'), ('IN EXCELLENT SHAPE', 'IN EXCELLENT SHAPE'), ('IN PERFECT SHAPE', 'IN PERFECT SHAPE'), ('IN NEW CONDITION', 'IN NEW CONDITION'), ('IN SHOWROOM CONDITION', 'IN SHOWROOM CONDITION')])),
                ('road_test', models.CharField()),
                ('fields', models.JSONField(blank=True, default=dict)),
                ('market_value', models.CharField()),
                ('forced_sale', models.CharField()),
                ('insurance_valuation', models.CharField(default='Not Applicable')),
                ('limiting_conditions', models.TextField(default='\nThis valuation report is made and or issued subject to the following terms and conditions:\nThis Valuation Report should only be used within the context of the instructions in which\nit is prepared i.e. to facilitate the internal loan approval processes of the lending institution.\nNeither the whole nor part of this valuation report nor any reference thereto may be included\nin any published document, circular or statement nor published in any form, without the\nwritten approval of Bik and Bos Ltd on the context it may appear.\nIn case the Lending institution intends to dispose of the subject motor vehicle as indicated\nherein, a new valuation exercise by a duly registered and or licensed valuer must be executed\nand at no time should this report be of reference since it serves a specific purpose of\nfacilitating the lending institution’s loan approval processes\nThe responsibility of Bik and Bos Ltd in connection with this report and valuation is limited\nto the lending institution to whom it is addressed. The valuer disclaims any responsibility\nand will accept no liability to any other party.\nThe Values are exclusive of all the encumbrances, any other factors not known to Bik and\nBos Ltd and those not considered in the valuation.\n                                           ')),
                ('effective_report_summary', models.TextField(default=' This report is made specifically for the internal consumption of the\nlending institution to enable it to execute its loan approval processes as per its Credit Policies\nand Procedures. It should not be used for any other purpose and or by any other consumer\nbesides the lending institution save for reference purposes. For any other purpose besides\nthe internal loan approval processes of the lending institution, we encourage that those\nconcerned carry out another valuation and assessment intended to serve the said purpose. ')),
                ('valuation', models.TextField(default='\nThe Valuation was based on the current day prices of the newly imported\nvehicles of the same type, model, capacity etc, plus relevant Government taxes, less\ndepreciation and by carrying out an open market inquiry with vehicles of similar type. We\ndefined depreciation being the measure of wearing out or loss of value of the vehicle /\nequipment either arising from effluxion of time or obsolescence through technology and\nmarket changes.\n    All other factors pertaining to depreciation and valuation calculations such as make, model,\nyear of manufacture, engine capacity, economical life span, mileage covered and particularly\nthe general mechanical condition was considered.\n\n')),
                ('market_value_description', models.TextField(default='\n        This being defined as the highest price a willing buyer would pay and\na willing seller would accept both being fully informed, and the property being exposed for sale\nfor a reasonable period of time or the price which a seller of the property would receive in an\nopen market by negotiations as distinguished from a distress price on forced or foreclosure sale\nor from an auction.\n')),
                ('current_value_description', models.TextField(default='\n        Having put into consideration all the necessary precautions, in our\nopinion, the "Relevant Values " to be used by the lending institution to internally make lending\ndecisions and or loan approval are as follows.\n')),
                ('recommendation', models.TextField(default='\n        The vehicle was in good condition and has a fair resale value. We, therefore, recommend\nit for the purpose of lending against it.\n\n')),
                ('right_hand_side_view', models.ImageField(upload_to='evaluation_report/right_hand_side_view/')),
                ('left_hand_eside_view', models.ImageField(upload_to='evaluation_report/left_hand_side_view/')),
                ('engine_compartment', models.ImageField(upload_to='evaluation_report/engine_compartment/')),
                ('upholstery', models.ImageField(upload_to='evaluation_report/upholstery/')),
                ('vehicle_id_plate', models.ImageField(upload_to='evaluation_report/vehicle_id_plate/')),
                ('company_valuer_remarks', models.TextField(blank=True, null=True)),
                ('company_supervisor_remarks', models.TextField(blank=True, null=True)),
                ('company_approver_remarks', models.TextField(blank=True, null=True)),
                ('slug', models.SlugField(blank=True, max_length=200, null=True, unique=True, verbose_name='Safe Url')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]