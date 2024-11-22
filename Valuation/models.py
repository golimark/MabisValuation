
from django.db import models
from django.utils import choices
from accounts.models import *
from django.core.validators import MinLengthValidator
from datetime import date
from django.core.exceptions import ValidationError
from django.utils.text import slugify
import uuid
from prospects.models import *

class VehicleAsset(models.Model):
    CAR_MAKES = [
        ('NISSAN', 'NISSAN'),
        ('TOYOTA', 'TOYOTA'),
        ('OTHER', 'OTHER'),
    ]

    FUEL_CHOICES = [
        ('DIESEL', 'DIESEL'),
        ('PETROL', 'PETROL'),
        ('ELECTRIC', 'ELECTRIC'),
    ]

    BODY_CHOICES = [
        ('SALOON', 'SALOON'),
        ('SUV', 'SUV'),
        ('STATION WAGON', 'STATION WAGON'),
        ('MINI-VAN', 'MINI-VAN'),
        ('SEDAN', 'SEDAN'),
        ('COUPE', 'COUPE'),
    ]

    STATUS = [
        ('NOT VALUED', 'NOT VALUED'),
        ('VALUED', 'VALUED'),
        ('IN TRACKING', 'IN TRACKING'),
        ('UNPOCESSED', 'UNPOCESSED'),
        ('REPOSESSED', 'REPOSESSED'),
        ('IMPOUNDED', 'IMPOUNDED'),
        ('SELF_PARKED', 'SELF_PARKED'),
        ('RECLAIMED', 'RECLAIMED'),
        ('DISPOSED_OFF', 'DISPOSED_OFF'),
    ]

    prospect = models.ForeignKey(to=Prospect, on_delete=models.SET_NULL, null=True, blank=True)
    logbook = models.CharField(max_length=256, null=True, blank=True)

    license_plate = models.CharField("Vehicle Registration Number", max_length=20)
    maketypes = models.CharField("Car Make Type", max_length=50, choices=CAR_MAKES, null=True, blank=True)
    make = models.CharField("Car Make", max_length=50, null=True, blank=True)
    model = models.CharField("Car Model", max_length=50, null=True, blank=True)
    # body_description = models.CharField("body description", max_length=200,  choices=BODY_CHOICES)
    
    # engine_number = models.CharField("engine number", max_length=50)
    # color_by_logbook = models.CharField("colour as per logbook", max_length=30)
    # color_by_inspection = models.CharField("colour as per inspection", max_length=30)
    # fuel_type = models.CharField("Fuel Type", max_length=10, choices=FUEL_CHOICES, null=True, blank=True)
    # year_of_manufacture = models.IntegerField("Year of manufacture",choices=[(i, i) for i in range(1900, 2023)], null=True)
    location = models.CharField("location of vehicle", max_length=255)
    
    status = models.CharField("Status", choices=STATUS, default="NOT VALUED")

    # fields to use by system
    slug = models.SlugField("Safe Url", unique=True, blank=True, null=True, max_length=200)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    @property
    def years_since_manufacture(self):
        if self.year_of_manufacture:
            return date.today().year - self.year_of_manufacture
        return None
    
    # def clean(self):
    #     # Validate that if 'make' is 'OTHER', 'custom_make' must be filled in.
    #     if self.make == 'OTHER' and not self.custom_make:
    #         raise ValidationError("Please provide a custom make if 'OTHER' is selected.")

    # def save(self, *args, **kwargs):
    #     self.full_clean()  # Ensure 'clean' is called on save
    #     super().save(*args, **kwargs)
        
    def save(self, *args, **kwargs):
        self.full_clean()  # Runs all validations defined in `clean`
        if not self.slug:
            self.slug = slugify(f"{self.license_plate}{uuid.uuid4()}")[:200]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.license_plate



class VehicleEvaluationReport(models.Model):
    
    REMARKS = [
        ('IN VERY BAD SHAPE','IN VERY BAD SHAPE'),
        ('IN BAD SHAPE','IN BAD SHAPE'),
        ('IN GOOD SHAPE','IN GOOD SHAPE'),
        ('IN VERY GOOD SHAPE','IN VERY GOOD SHAPE'),
        ('IN EXCELLENT SHAPE','IN EXCELLENT SHAPE'),
        ('IN PERFECT SHAPE','IN PERFECT SHAPE'),
        ('IN NEW CONDITION','IN NEW CONDITION'),
        ('IN SHOWROOM CONDITION','IN SHOWROOM CONDITION'),
    ]

    BODY_CHOICES = [
        ('SALOON', 'SALOON'),
        ('SUV', 'SUV'),
        ('STATION WAGON', 'STATION WAGON'),
        ('MINI-VAN', 'MINI-VAN'),
        ('SEDAN', 'SEDAN'),
        ('COUPE', 'COUPE'),
    ]
    FUEL_CHOICES = [
        ('DIESEL', 'DIESEL'),
        ('PETROL', 'PETROL'),
        ('ELECTRIC', 'ELECTRIC'),
        ]
    
    GEARBOX_CHOICES = [
        ('AUTOMATIC', 'AUTOMATIC'),
        ('MANUAL', 'MANUAL'),
        ('HYBRID', 'HYBRID'),
        ('ELECTRIC', 'ELECTRIC'),
    ]
    
    vehicle = models.ForeignKey(to=VehicleAsset, on_delete=models.SET_NULL, null=True, blank=True)
    prospect = models.ForeignKey(Prospect, on_delete=models.CASCADE)

    name_in_logbook = models.CharField(max_length=100, default=prospect.name)
    tax_identification_number = models.CharField(max_length=50)

    # Vehicle condition-related fields
    date_of_registration = models.DateField("date of registration", null=True)
    make = models.CharField("Car Make", max_length=50, null=True, blank=True)
    model = models.CharField("Car Model", max_length=50, null=True, blank=True)
    body_description = models.CharField("body description", max_length=200,  choices=BODY_CHOICES, null=True)   
    color_by_logbook = models.CharField("colour as per logbook", max_length=30, null=True)
    fuel_type = models.CharField("Fuel Type", max_length=10, choices=FUEL_CHOICES, null=True, blank=True)    
    mileage = models.IntegerField("milage", null=True)
    power = models.IntegerField("Power(cubic capacity)", null=True, blank=True)  # You can specify units like horsepower or kilowatts in the form
    gearbox_transmission = models.CharField("Gear box transmission", max_length=50, choices=GEARBOX_CHOICES, null=True)
    engine_number = models.CharField("engine number", max_length=50, null=True)
    chassis_number = models.CharField("chassis number", max_length=50, null=True)
    country_of_origin = models.CharField("Country of origin", max_length=50, null=True)
    year_of_manufacture = models.IntegerField("Year of manufacture",choices=[(i, i) for i in range(1998, 2023)], null=True)
    # years_since_manufacture = models.IntegerField("years since manufacture", null=True, blank=True)
    years_since_on_uganda_roads = models.IntegerField("years since on uganda roads", null=True)
    seating_capacity = models.IntegerField(null=True, blank=True, default=0)
    place_of_inspection = models.CharField(max_length=100)
    date_of_valuation = models.DateTimeField()
    valuation_report_date = models.DateField()
    color_by_inspection = models.CharField("colour as per inspection", max_length=30, null=True, blank=True)
    chassis_frame = models.CharField(choices=REMARKS, max_length=100)
    body_shell_paint = models.CharField(choices=REMARKS, max_length=100)
    condition_of_seats = models.CharField(choices=REMARKS)
    engine_assembly = models.CharField(choices=REMARKS)
    accessories = models.CharField(choices=REMARKS,max_length=100)
    cooling_system = models.CharField(choices=REMARKS)
    gearbox_assembly = models.CharField(choices=REMARKS)
    transmission_system = models.CharField(choices=REMARKS)
    steering_system = models.CharField(choices=REMARKS)
    suspension = models.CharField(choices=REMARKS)
    braking_system = models.CharField(choices=REMARKS)
    electrical_system = models.CharField(choices=REMARKS)
    windshield = models.CharField(choices=REMARKS)
    air_conditioning_system = models.CharField(choices=REMARKS)
    wheels = models.CharField(choices=REMARKS)
    tyre_condition = models.CharField(choices=REMARKS)
    road_test = models.CharField()
    fields = models.JSONField(default=dict, blank=True)
    # changed these from decimal to charlfield
    market_value = models.CharField()
    forced_sale = models.CharField()
    insurance_valuation = models.CharField(default='Not Applicable')
    # end
    limiting_conditions = models.TextField( default="""
This valuation report is made and or issued subject to the following terms and conditions:
This Valuation Report should only be used within the context of the instructions in which
it is prepared i.e. to facilitate the internal loan approval processes of the lending institution.
Neither the whole nor part of this valuation report nor any reference thereto may be included
in any published document, circular or statement nor published in any form, without the
written approval of Bik and Bos Ltd on the context it may appear.
In case the Lending institution intends to dispose of the subject motor vehicle as indicated
herein, a new valuation exercise by a duly registered and or licensed valuer must be executed
and at no time should this report be of reference since it serves a specific purpose of
facilitating the lending institution’s loan approval processes
The responsibility of Bik and Bos Ltd in connection with this report and valuation is limited
to the lending institution to whom it is addressed. The valuer disclaims any responsibility
and will accept no liability to any other party.
The Values are exclusive of all the encumbrances, any other factors not known to Bik and
Bos Ltd and those not considered in the valuation.
                                           """)
    effective_report_summary = models.TextField( default=""" This report is made specifically for the internal consumption of the
lending institution to enable it to execute its loan approval processes as per its Credit Policies
and Procedures. It should not be used for any other purpose and or by any other consumer
besides the lending institution save for reference purposes. For any other purpose besides
the internal loan approval processes of the lending institution, we encourage that those
concerned carry out another valuation and assessment intended to serve the said purpose. """)
    valuation = models.TextField(default="""
The Valuation was based on the current day prices of the newly imported
vehicles of the same type, model, capacity etc, plus relevant Government taxes, less
depreciation and by carrying out an open market inquiry with vehicles of similar type. We
defined depreciation being the measure of wearing out or loss of value of the vehicle /
equipment either arising from effluxion of time or obsolescence through technology and
market changes.
    All other factors pertaining to depreciation and valuation calculations such as make, model,
year of manufacture, engine capacity, economical life span, mileage covered and particularly
the general mechanical condition was considered.

""")
    market_value_description = models.TextField(default="""
        This being defined as the highest price a willing buyer would pay and
a willing seller would accept both being fully informed, and the property being exposed for sale
for a reasonable period of time or the price which a seller of the property would receive in an
open market by negotiations as distinguished from a distress price on forced or foreclosure sale
or from an auction.
""")
    current_value_description = models.TextField(default="""
        Having put into consideration all the necessary precautions, in our
opinion, the "Relevant Values " to be used by the lending institution to internally make lending
decisions and or loan approval are as follows.
""")
    recommendation = models.TextField(default="""
        The vehicle was in good condition and has a fair resale value. We, therefore, recommend
it for the purpose of lending against it.

""")

    front_right_hand_side_view= models.ImageField(upload_to='evaluation_report/right_hand_side_view/')
    front_left_hand_eside_view= models.ImageField(upload_to='evaluation_report/left_hand_side_view/')
    back_right_hand_side_view= models.ImageField(upload_to='evaluation_report/right_hand_side_view/', null=True, blank=True)
    back_left_hand_side_view= models.ImageField(upload_to='evaluation_report/right_hand_side_view/', null=True, blank=True)
    engine_compartment= models.ImageField(upload_to='evaluation_report/engine_compartment/')
    upholstery= models.ImageField(upload_to='evaluation_report/upholstery/')
    vehicle_id_plate= models.ImageField(upload_to='evaluation_report/vehicle_id_plate/')

    #VALUATION REMARKS
    #VALUER 
    company_valuer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='company_valuer')
    company_valuer_remarks = models.TextField(null=True, blank=True)

    #SUPERVISOR
    company_supervisor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='company_supervisor')
    company_supervisor_remarks = models.TextField(null=True, blank=True)

    #APPROVER 
    company_approver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='company_approver')
    company_approver_remarks = models.TextField(null=True, blank=True)


    # valuation_location = models.CharField(max_length=255)
    # valuation_company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='valuation_reports')

    slug = models.SlugField("Safe Url", unique=True, blank=True, null=True, max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    
    def clean(self):
        # Ensure date_of_registration is not earlier than year_of_manufacture
        if self.date_of_registration and self.year_of_manufacture:
            if self.date_of_registration.year < self.year_of_manufacture:
                raise ValidationError("The date of registration cannot be earlier than the year of manufacture.")

        # Ensure years_since_on_uganda_roads does not exceed time since date_of_registration
        if self.date_of_registration and self.years_since_on_uganda_roads is not None:
            years_registered = date.today().year - self.date_of_registration.year
            if self.years_since_on_uganda_roads > years_registered:
                raise ValidationError("Years since on Uganda roads cannot exceed the time since registration.")



    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.vehicle.license_plate}{uuid.uuid4()}")[:200]
        super().save(*args, **kwargs)

        # update asset status
        self.vehicle.status = "VALUED"
        self.vehicle.save()


    @property
    def years_on_road(self):
        if self.vehicle.years_since_on_uganda_roads:
            return date.today().year - self.vehicle.years_since_on_uganda_roads
        return None

    @property
    def years_since_manufacture(self):
        if self.year_of_manufacture:
            return date.today().year - self.year_of_manufacture
        return None
    
    def __str__(self):
        return f"Evaluation Report for {self.prospect.name} ({self.vehicle.license_plate})"


class LandAsset(models.Model):
    land_location = models.CharField("LAND LOCATION")
    prospect = models.ForeignKey(to=Prospect, on_delete=models.SET_NULL, null=True, blank=True)
    landtitle = models.FileField(upload_to='prospect/landtitle/', null=True, blank=True)


    slug = models.SlugField("Safe Url", unique=True, blank=True, null=True, max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.license_plate}{uuid.uuid4()}")[:200]
        super().save(*args, **kwargs)

class LandEvaluationReport(models.Model):
    land = models.ForeignKey(to=LandAsset, on_delete=models.SET_NULL, null=True, blank=True)
    prospect = models.ForeignKey(Prospect, on_delete=models.CASCADE)

    slug = models.SlugField("Safe Url", unique=True, blank=True, null=True, max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.license_plate}{uuid.uuid4()}")[:200]
        super().save(*args, **kwargs)
