from enum import UNIQUE
from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils.text import slugify
import uuid



class LoanCompany(models.Model):
    name = models.CharField(max_length=255)
    api = models.URLField()
    api_key = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.api and self.api.endswith('/'):
            self.api = self.api[:-1]
        super().save(*args, **kwargs)




class Company(models.Model):
    class Meta:
        ordering = ['-updated_at']

    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='company_logo/', null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    code = models.CharField(max_length=100, default='1101')
    slug = models.SlugField("Safe Url", unique=True, blank=True, null=True, max_length=200)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    active = models.ForeignKey(LoanCompany, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'{self.name}'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.name}{uuid.uuid4()}")[:200]

        super().save(*args, **kwargs)

# system defined permissions e.g. Can Create Agent
class Permission(models.Model):
    class Meta:
        ordering = ['-updated_at']

    name = models.CharField(max_length=100, help_text="Follow format e.g. 'Can Create Agent'", blank=True, null=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        # make lowercase, remove all spaces
        if self.name:
            self.code = "_".join(self.name.lower().split(" "))

        if self.code and not self.name:
            self.name = " ".join(self.code.split("_"))

        if not self.description:
            self.description = f"User {self.name}"
        # save as can_create_agent
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Role(models.Model):
    class Meta:
        ordering = ['-updated_at']

    name = models.CharField(max_length=100)
    permissions = models.ManyToManyField(Permission, related_name='roles')
    # each company has its own roles
    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    slug = models.SlugField("Safe Url", unique=True, blank=True, null=True, max_length=200)

    def __str__(self):
        try:
            return f"{self.name} - {self.company}"
        except:
            return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.name}{uuid.uuid4()}")[:200]

        super().save(*args, **kwargs)


class User(AbstractUser):
    class Meta:
        ordering = ['-updated_at']

    STATUS_CHOICES = [
            ('Pending', 'Pending'),
            ('Approved', 'Approved'),
            ('Rejected', 'Rejected'),
        ]

    email = models.EmailField("user email", blank=True, null=True)
    companies = models.ManyToManyField(Company, related_name="companies")
    active_company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=True, null=True)
    updated_on = models.DateTimeField("Updated on", auto_now=True)
    role = models.ForeignKey("Role", on_delete=models.CASCADE, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Approved')
    image = models.ImageField(upload_to='accounts/user/', null=True, blank=True)
    slug = models.SlugField("Safe Url", unique=True, blank=True, null=True, max_length=200)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        if not (self.first_name and self.last_name):
            return f"{self.username}"
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        self.slug = slugify(f"{self.first_name}-{self.last_name}-{uuid.uuid4()}")[:200]

        if self.pk and not self.active_company and self.companies.all():
            self.active_company = self.companies.first()

        super().save(*args, **kwargs)

    @property
    def company(self):
        return self.active_company

    @property
    def permissions(self):
        if self.role:
            return [permission.code for permission in self.role.permissions.all()]
        return []

    @property
    def name(self):
        if not (self.first_name and self.last_name):
            return f"{self.username}"
        return f"{self.first_name} {self.last_name}"
