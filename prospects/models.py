from django.db import models
from django.utils import choices
from accounts.models import *
from django.core.validators import MinLengthValidator
from datetime import date
from django.core.exceptions import ValidationError
from django.utils.text import slugify
import uuid


class CarType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class CarModel(models.Model):
    name = models.CharField(max_length=50)
    model_name = models.ForeignKey('CarType', on_delete=models.CASCADE, related_name='models')

    def __str__(self):
        return self.name


def validate_phone_number(value):
    if len(value) != 10 or not value.startswith('0'):
        raise ValidationError(
            f'{value} is not a valid phone number. It must start with 07 and be exactly 10 digits long.'
        )


class Prospect(models.Model):
    GENDER_CHOICES = [
        ('MALE', 'MALE'),
        ('FEMALE', 'FEMALE'),
    ]
    STATUS_CHOICES = [
        ('New', 'New'),
        ('Pending', 'Pending'),
        ('Valuation', 'Valuation'),
        ('Valuation Supervisor', 'Valuation Supervisor'),
        ('Payment Verified', 'Payment Verified'),
        ('Inspection', 'Inspection'),
        ('Review', 'Review'),
        ('Pipeline', 'Pipeline'),
        ('Failed', 'Failed'),
        ('Declined', 'Declined'),
    ]
    TITLE_CHOICES = [
        ('MS.', 'MS.'),
        ('MR.', 'MR.'),
    ]
    # added company field
    company = models.CharField(max_length=256)
    name = models.CharField("NAME", max_length=255)
    gender = models.CharField("GENDER", max_length=10, choices=GENDER_CHOICES)
    phone_number = models.CharField("PHONE NUMBER", max_length=10, validators=[validate_phone_number])
    email = models.EmailField("EMAIL", null=True, blank=True)
    title = models.CharField("TITLE", choices=TITLE_CHOICES)
    alt_number = models.CharField("OTHER PHONE NUMBER", max_length=10, blank=True, null=True, validators=[validate_phone_number])
    agent = models.CharField(max_length=256)
    date_of_birth = models.DateField("DATE OF BIRTH", null=True, blank=True)
    created_by = models.CharField(max_length=256)
    decline_reason = models.CharField(max_length=255, null=True, blank=True)

    # Loan details
    proof_of_payment = models.URLField(null=True, blank=True)
    # proof_of_payment = models.CharField(max_length=256, null=True, blank=True)
    proof_of_payment_id = models.CharField("PROOF OF PAYMENT ID", max_length=50, null=True, blank=True)
    # proof_of_payment_id = models.CharField("PROOF OF PAYMENT ID", max_length=50, null=True, blank=True, unique=True)
    status = models.CharField("STATUS", max_length=20, choices=STATUS_CHOICES, default='New', null=True, blank=True)
    slug = models.SlugField("Safe Url", unique=True, blank=True, null=True, max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    asset_submitted_on = models.DateTimeField(blank=True, null=True)
    asset_submitted_by = models.CharField(max_length=256, null=True, blank=True)

    payment_verified_on = models.DateTimeField(blank=True, null=True)
    payment_verified_by = models.CharField(max_length=256, null=True, blank=True)

    submitted_for_valuation_on = models.DateTimeField(blank=True, null=True)
    submitted_for_valuation_by = models.CharField(max_length=256, null=True, blank=True)

    # valuer assigned
    valuer_assigned_on = models.DateTimeField(blank=True, null=True)
    valuer_assigned = models.CharField(max_length=256, null=True, blank=True)

    # valuation supervisor
    valuation_submitted_on = models.DateTimeField(blank=True, null=True)
    valuation_submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="valuation_submitted_by")

    # valuation Approver
    valuation_reviewd_on = models.DateTimeField(blank=True, null=True)
    valuation_reviewd_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="valuation_reviewd_by")


    # def clean(self):
    #     # Check if proof_of_payment_id is unique
    #     if Prospect.objects.filter(proof_of_payment_id=self.proof_of_payment_id).exclude(id=self.id).exists():
    #         raise ValidationError({"proof_of_payment_id": "This Proof of Payment ID already exists. Please provide a unique ID."})


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.name}{uuid.uuid4()}")[:200]

        if self.gender == "FEMALE":
            self.title = "MS."
        elif self.gender == "MALE":
            self.title = "MR."


        # to cater for api

        if isinstance(self.valuation_submitted_by, str):
            user = User.objects.filter(name=self.self.valuation_submitted_by)
            if user:
                self.valuation_submitted_by = user
            else:
                self.valuation_submitted_by = None
                

        if isinstance(self.valuation_reviewd_by, str):
            user = User.objects.filter(name=self.self.valuation_reviewd_by)
            if user:
                self.valuation_reviewd_by = user
            else:
                self.valuation_reviewd_by = None

        super().save(*args, **kwargs)

    @property
    def age(self):
        if self.date_of_birth:
            return date.today().year - self.date_of_birth.year
        return "Not Set"

    def __str__(self):
        return self.name

REMARKS = [
    ('IN VERY BAD SHAPE','IN VERY BAD SHAPE'),
    ('IN BAD SHAPE','IN BAD SHAPE'),
    ('IN FAIR SHAPE', 'IN FAIR SHAPE'),
    ('IN GOOD SHAPE','IN GOOD SHAPE'),
    ('IN VERY GOOD SHAPE','IN VERY GOOD SHAPE'),
    ('IN EXCELLENT SHAPE','IN EXCELLENT SHAPE'),
    ('IN PERFECT SHAPE','IN PERFECT SHAPE'),
    ('IN NEW CONDITION','IN NEW CONDITION'),
    ('IN SHOWROOM CONDITION','IN SHOWROOM CONDITION'),
]

