from django.core.validators import RegexValidator
from django.db import models

import phonenumbers
from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.

class Project(models.Model):
    project_name = models.CharField(max_length=200)
    project_location = models.CharField(max_length=200)
    project_manager = models.CharField(max_length=200)
    project_number = models.CharField(max_length=9, validators=[RegexValidator(r'^\d{0,9}$')])
    project_writeup = models.TextField(null=True, blank=True)
    client_name = models.CharField(max_length=200)
    client_contact = models.CharField(max_length=200, null=True, blank=True)
    client_phone = PhoneNumberField(null=True, blank=True)
    client_email = models.EmailField(max_length=200, null=True, blank=True)
    des_start_date = models.DateTimeField('design start date', null=True, blank=True)
    des_end_date = models.DateTimeField('design end date', null=True, blank=True)
    con_start_date = models.DateTimeField('construction start date', null=True, blank=True)
    con_end_date = models.DateTimeField('construction end date', null=True, blank=True)
    con_cost = models.DecimalField('construction cost', max_digits=12, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return self.project_name

    def get_absolute_url(self):
        return f"/projects/{self.id}/"

    def formatted_phone(self, country=None):
        return phonenumbers.parse(self.client_phone, country)