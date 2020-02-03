""" Models for Projects app """
from django.core.validators import MaxLengthValidator, \
    MinLengthValidator, RegexValidator, validate_email
from django.db import models

class Project(models.Model):
    """ Model definition for a Project """
    project_name = models.CharField(max_length=200)
    project_location = models.CharField(max_length=200)
    project_manager = models.CharField(max_length=200)
    project_number = models.CharField(max_length=9, validators=[RegexValidator(r'^\d{0,9}$')])
    client_name = models.CharField('client', max_length=200)
    client_contact = models.CharField(max_length=200, null=True, blank=True)
    client_phone = models.CharField(
        max_length=10, null=True, blank=True,
        validators=[MinLengthValidator(10), MaxLengthValidator(10)])
    client_email = models.EmailField(
        max_length=200, null=True, blank=True, validators=[validate_email])
    des_start_date = models.DateField('design start date', null=True, blank=True)
    des_end_date = models.DateField('design end date', null=True, blank=True)
    des_fee = models.IntegerField('design fee', null=True, blank=True)
    con_start_date = models.DateField('construction start date', null=True, blank=True)
    con_end_date = models.DateField('construction end date', null=True, blank=True)
    con_cost = models.IntegerField('construction cost', null=True, blank=True)

    def __str__(self):
        return self.project_name

    def get_absolute_url(self):
        """ Returns absolute URL of project instance """
        return f"/projects/{self.id}/"

class Writeup(models.Model):
    """ Model definition for project writeups """
    class Meta:
        ordering = ('pk', '-date_added')

    focus = models.CharField(max_length=200)
    project_writeup = models.TextField(null=True, blank=True)
    date_added = models.DateTimeField(null=True, blank=True)
    project = models.ForeignKey(Project, related_name='writeups', on_delete=models.CASCADE)

    def __str__(self):
        return "Writeup " + str(self.pk)

    __str__.admin_order_field = "pk"
