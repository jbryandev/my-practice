"""
Defines the various admin models for this application.
"""
from django.contrib import admin
from django.forms import ModelChoiceField
from .models import Project, Writeup

# Register your models here.

class ProjectAdmin(admin.ModelAdmin):
    """ Admin model for Writeup class """
    list_display = ('project_name', 'client_name', 'project_location')
    list_filter = ['des_end_date']
    search_fields = ['project_name']

class WriteupAdmin(admin.ModelAdmin):
    """ Admin model for Writeup class """
    ordering = ['pk']
    list_display = ('__str__', 'get_project', 'focus', 'date_added')
    list_filter = ['date_added']

    def get_queryset(self, request):
        # Joins Project to query
        return super(WriteupAdmin, self).get_queryset(
            request).select_related('project')

    def get_project(self, obj):
        """ Gets the project of a particular writeup """
        return obj.project

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "writeup":
            return WriteupChoiceField(queryset=Writeup.objects.all())
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    get_project.admin_order_field = 'writeup__project_name' #Allows column order sorting
    get_project.short_description = 'Project'  #Renames column heading

class WriteupChoiceField(ModelChoiceField):
    """
    Override default ModelChoiceField to add Project to label.
    """
    def label_from_instance(self, obj):
        return "{} ({})".format(obj, obj.project)

admin.site.register(Project, ProjectAdmin)
admin.site.register(Writeup, WriteupAdmin)
