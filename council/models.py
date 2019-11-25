from django.db import models
from django.urls import reverse
from django.utils import timezone
from datetime import datetime

# Create your models here.
class Agency(models.Model):
    class Meta:
        verbose_name_plural = "agencies"
        ordering = ('agency_name', 'date_added')

    agency_name = models.CharField(max_length=200)
    date_added = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return self.agency_name

    def get_absolute_url(self):
        return reverse('council:agency-detail', args=[str(self.id)])

class Department(models.Model):
    class Meta:
        ordering = ('agency', 'department_name')

    department_name = models.CharField(max_length=200)
    date_added = models.DateTimeField(null=True, blank=True)
    meeting_info = models.TextField(null=True, blank=True) # Put general meeting info here (location, time, frequency)
    agendas_url = models.URLField(null=True, blank=True, max_length=500)
    agency = models.ForeignKey(Agency, related_name='departments', on_delete=models.CASCADE)

    def __str__(self):
        return self.department_name

    def get_absolute_url(self):
        return reverse('council:department-detail', args=[str(self.id)])

class Agenda(models.Model):
    class Meta:
        ordering = ('department__agency_name', 'department', 'agenda_date')

    agenda_date = models.DateField(null=False, blank=False) # a.k.a. date of meeting
    agenda_title = models.CharField(null=True, blank=True, max_length=200) # meeting title (Council Meeting, Trust, etc.)
    agenda_url = models.URLField(null=True, blank=True, max_length=500) # URL path to agenda
    agenda_text = models.TextField(null=True, blank=True) # Crawler will populate this field automatically
    pdf_link = models.URLField(null=True, blank=True, max_length=500) # Separate link to PDF for instances where agenda url is html
    date_added = models.DateTimeField(null=True, blank=True) # Date agenda was added to db
    department = models.ForeignKey(Department, related_name='agendas', on_delete=models.CASCADE)

    def __str__(self):
        return self.agenda_date.strftime("%x")

    def get_absolute_url(self):
        return reverse('council:agenda-detail', args=[str(self.id)])

class Crawler(models.Model):
    crawler_name = models.CharField(max_length=200)
    date_added = models.DateTimeField(null=True, blank=True)
    department = models.ManyToManyField(Department, related_name='crawlers')

    def __str__(self):
        return self.crawler_name