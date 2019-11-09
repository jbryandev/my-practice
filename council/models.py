from django.db import models

# Create your models here.
class Agency(models.Model):
    agency_name = models.CharField(max_length=200)
    
    def __str__(self):
        return self.agency_name