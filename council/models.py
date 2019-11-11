from django.db import models
from datetime import datetime
import requests
import io
from pdf2image import convert_from_bytes
import pytesseract
from PIL import Image

# Create your models here.
class Agency(models.Model):
    class Meta:
        verbose_name_plural = "agencies"
        ordering = ('agency_name', 'date_added')

    agency_name = models.CharField(max_length=200)
    date_added = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return self.agency_name

class Department(models.Model):
    class Meta:
        ordering = ('agency', 'department_name')

    department_name = models.CharField(max_length=200)
    date_added = models.DateTimeField(null=True, blank=True)
    meeting_info = models.TextField(null=True, blank=True)
    agency = models.ForeignKey(Agency, related_name='departments', on_delete=models.CASCADE)

    def __str__(self):
        return self.department_name

class Agenda(models.Model):
    class Meta:
        ordering = ('department', 'agenda_date')

    agenda_date = models.DateField(null=False, blank=False)
    date_added = models.DateTimeField(null=True, blank=True)
    pdf_link = models.URLField(null=True, blank=True, max_length=500)
    department = models.ForeignKey(Department, related_name='agendas', on_delete=models.CASCADE)

    def __str__(self):
        return self.agenda_date.strftime("%x")

    def get_text(self):
        text = ""
        r = requests.get(self.pdf_link)
        f = io.BytesIO(r.content)
        images = convert_from_bytes(f.read())
        for image in images:
            text += str(((pytesseract.image_to_string(image)))) 
        return text