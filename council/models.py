from django.db import models
from django.urls import reverse
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

    def get_absolute_url(self):
        return reverse('council:agency-detail', args=[str(self.id)])

class Department(models.Model):
    class Meta:
        ordering = ('agency', 'department_name')

    department_name = models.CharField(max_length=200)
    date_added = models.DateTimeField(null=True, blank=True)
    meeting_info = models.TextField(null=True, blank=True)
    agency = models.ForeignKey(Agency, related_name='departments', on_delete=models.CASCADE)

    def __str__(self):
        return self.department_name

    def get_absolute_url(self):
        return reverse('council:department-detail', args=[str(self.id)])

class Agenda(models.Model):
    class Meta:
        ordering = ('department', 'agenda_date')

    agenda_date = models.DateField(null=False, blank=False)
    date_added = models.DateTimeField(null=True, blank=True)
    pdf_link = models.URLField(null=True, blank=True, max_length=500)
    agenda_text = models.TextField(null=True, blank=True)
    department = models.ForeignKey(Department, related_name='agendas', on_delete=models.CASCADE)

    def __str__(self):
        return self.agenda_date.strftime("%x")

    def get_absolute_url(self):
        return reverse('council:agenda-detail', args=[str(self.id)])

    def pdf2text(self, pdf_url):
        # Takes a URL of a PDF and converts the PDF to text using tesseract
        # Returns the converted text as a string
        pdf_text = ""
        r = requests.get(pdf_url)
        f = io.BytesIO(r.content)
        images = convert_from_bytes(f.read())
        for image in images:
            pdf_text += str(((pytesseract.image_to_string(image)))) 
        return pdf_text

    def get_text(self):
        if not self.agenda_text:
            print("Agenda has not been converted to text yet. Attempting to convert from PDF...")
            self.agenda_text = self.pdf2text(self.pdf_link)
            self.save(update_fields=['agenda_text'])
            return self.agenda_text
        else:
            print("Agenda has already been converted to text from PDF. Displaying resulting text.")
            return self.agenda_text