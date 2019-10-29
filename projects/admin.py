from django.contrib import admin

from .models import Project

# Register your models here.

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('project_name', 'client_name','project_location')
    list_filter = ['des_end_date']
    search_fields = ['project_name']

admin.site.register(Project, ProjectAdmin)