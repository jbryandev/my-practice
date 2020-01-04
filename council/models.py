"""
This defines the models used in the council app
"""
from django.db import models
from django.urls import reverse

# Create your models here.
class Agency(models.Model):
    """ An agency contains many departments. """
    class Meta:
        verbose_name_plural = "agencies"
        ordering = ('agency_name', 'date_added')

    agency_name = models.CharField(max_length=200)
    date_added = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.agency_name

    def get_absolute_url(self):
        """ Returns absolute URL of agency. """
        return reverse('council:agency-detail', args=[str(self.id)])

class Department(models.Model):
    """ A department belongs to an agency and has agendas. """
    class Meta:
        ordering = ('agency', 'department_name')

    department_name = models.CharField(max_length=200)
    date_added = models.DateTimeField(null=True, blank=True)
    # Put general meeting info here (location, time, frequency)
    meeting_info = models.TextField(null=True, blank=True)
    agendas_url = models.URLField(null=True, blank=True, max_length=500)
    agency = models.ForeignKey(Agency, related_name='departments', on_delete=models.CASCADE)

    def __str__(self):
        return self.department_name

    def get_absolute_url(self):
        """ Return absolute URL of department. """
        return reverse('council:department-detail', args=[str(self.id)])

class Agenda(models.Model):
    """ An agenda belongs to a specific department. """
    class Meta:
        ordering = ('department__agency_name', 'department', 'agenda_date')

    agenda_date = models.DateField(null=False, blank=False)
    agenda_title = models.CharField(null=True, blank=True, max_length=200)
    agenda_url = models.URLField(null=True, blank=True, max_length=500)
    agenda_text = models.TextField(null=True, blank=True)
    pdf_link = models.URLField(null=True, blank=True, max_length=500)
    date_added = models.DateTimeField(null=True, blank=True)
    department = models.ForeignKey(Department, related_name='agendas', on_delete=models.CASCADE)

    def __str__(self):
        return self.agenda_date.strftime("%x")

    def get_absolute_url(self):
        """ Return absolute URL of agenda. """
        return reverse('council:agenda-detail', args=[str(self.id)])

class Crawler(models.Model):
    """
    A crawler is the vehicle for scraping agenda data from the web.
    A crawler can belong to multiple departments.
    """
    class Meta:
        ordering = ('crawler_name', 'date_added')

    crawler_name = models.CharField(max_length=200)
    date_added = models.DateTimeField(null=True, blank=True)
    department = models.ManyToManyField(Department, related_name='crawlers')

    def __str__(self):
        return self.crawler_name

class Highlight(models.Model):
    """
    A highlight marks relevant portions of an agenda.
    It is marked by a start and end string position within the agenda.
    A highlight belongs to only one agenda, but an agenda can have many highlights.
    """

    date_added = models.DateTimeField(null=True, blank=True)
    hl_start = models.PositiveIntegerField("highlight start")
    hl_end = models.PositiveIntegerField("highlight end")
    hl_category = models.CharField("category", max_length=200, null=True, blank=True)
    agenda = models.ForeignKey(Agenda, related_name='highlights', on_delete=models.CASCADE)

    def __str__(self):
        return "Highlight " + str(self.pk)

    __str__.admin_order_field = "pk"
