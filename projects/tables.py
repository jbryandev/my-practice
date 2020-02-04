""" Table definition for Projects table """
import django_tables2 as tables
from .models import Project

class ProjectTable(tables.Table):
    """ Class for Projects index table """
    project_name = tables.Column(linkify=True)

    class Meta:
        """ Meta class for Projects index table """
        model = Project
        template_name = "django_tables2/bootstrap4.html"
        fields = ("project_name", "client_name", "project_location")
        attrs = {
            "class": "table table-striped"
        }
