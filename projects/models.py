from django.db import models

# Create your models here.

class Project(models.Model):
    project_name = models.CharField(max_length=200)
    client_name = models.CharField(max_length=200)
    start_date = models.DateTimeField('start date')
    end_date = models.DateTimeField('end date')
    project_location = models.CharField(max_length=200)
    project_number = models.CharField(max_length=10)
    project_manager = models.CharField(max_length=200)
    project_writeup = models.TextField()
    def __str__(self):
        return self.project_name