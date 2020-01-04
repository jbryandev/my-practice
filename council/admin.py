"""
Defines the various admin models for this application.
"""
from django.contrib import admin
from django.forms import ModelChoiceField, ModelMultipleChoiceField
from .models import Agency, Department, Agenda, Crawler, Highlight

# Register your models here.

class AgencyAdmin(admin.ModelAdmin):
    """ Admin model for Agency class """
    list_display = ('agency_name', 'date_added')
    list_filter = ['date_added']
    search_fields = ['agency_name']

class DepartmentAdmin(admin.ModelAdmin):
    """ Admin model for Department class """
    list_display = ('department_name', 'agency', 'date_added')
    list_filter = ['date_added']
    search_fields = ['department_name']

class AgendaAdmin(admin.ModelAdmin):
    """ Admin model for Agenda class """
    list_display = ('agenda_date', 'agenda_title', 'department', 'get_agency')
    list_filter = ['agenda_date']

    def get_queryset(self, request):
        # Joins department and agency to query
        return super(AgendaAdmin, self).get_queryset(request).select_related('department__agency')

    def get_agency(self, obj):
        """ Gets the agency of a particular department """
        return obj.department.agency

    get_agency.admin_order_field = 'department__agency_name' #Allows column order sorting
    get_agency.short_description = 'Agency'  #Renames column heading

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "department":
            return DepartmentChoiceField(queryset=Department.objects.all())
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class CrawlerAdmin(admin.ModelAdmin):
    """ Admin model for Crawler class """
    list_display = ('crawler_name', 'date_added')
    list_filter = ['date_added']
    search_fields = ['crawler_name']

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "department":
            return DepartmentMultipleChoiceField(queryset=Department.objects.all())
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class HighlightAdmin(admin.ModelAdmin):
    """ Admin model for Highlight class """
    ordering = ['pk']
    list_display = ('__str__', 'hl_category', 'get_agency', 'get_department')
    list_filter = ['hl_category']

    def get_queryset(self, request):
        # Joins department and agency to query
        return super(HighlightAdmin, self).get_queryset(
            request).select_related('agenda__department__agency')

    def get_department(self, obj):
        """ Gets the department of a particular agenda """
        return obj.agenda.department

    def get_agency(self, obj):
        """ Gets the agency of a particular department """
        return obj.agenda.department.agency

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "agenda":
            return AgendaChoiceField(queryset=Agenda.objects.all())
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    get_department.admin_order_field = 'agenda__department_name' #Allows column order sorting
    get_department.short_description = 'Department'  #Renames column heading
    get_agency.admin_order_field = 'department__agency_name' #Allows column order sorting
    get_agency.short_description = 'Agency'  #Renames column heading

class DepartmentChoiceField(ModelChoiceField):
    """
    Override default ModelChoiceField to add Agency to Department label.
    This prevents confusion when multiple Agencies have same Department names.
    """
    def label_from_instance(self, obj):
        return "{} ({})".format(obj, obj.agency)

class DepartmentMultipleChoiceField(ModelMultipleChoiceField):
    """
    Override default ModelMultipleChoiceField to add Agency to Department label.
    This prevents confusion when multiple Agencies have same Department names.
    """
    def label_from_instance(self, obj):
        return "{} ({})".format(obj, obj.agency)

class AgendaChoiceField(ModelChoiceField):
    """
    Override default ModelChoiceField to add Agency and Department to label.
    """
    def label_from_instance(self, obj):
        return "{} {} ({} - {})".format(
            obj, obj.agenda_title, obj.department.agency, obj.department)

admin.site.register(Agency, AgencyAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Agenda, AgendaAdmin)
admin.site.register(Crawler, CrawlerAdmin)
admin.site.register(Highlight, HighlightAdmin)
