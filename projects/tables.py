import django_tables2 as tables

from .models import Project

class ProjectTable(tables.Table):
    project_name = tables.Column(linkify=True)

    class Meta:
        model = Project
        template_name = "django_tables2/bootstrap.html"
        fields = ("project_name", "client_name", "project_location")