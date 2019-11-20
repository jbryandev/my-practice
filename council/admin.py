from django.contrib import admin
from django.forms import ModelChoiceField

from .models import Agency, Department, Agenda

# Register your models here.

class AgencyAdmin(admin.ModelAdmin):
    list_display = ('agency_name', 'date_added')
    list_filter = ['date_added']
    search_fields = ['agency_name']

class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('department_name', 'agency', 'date_added')
    list_filter = ['date_added']
    search_fields = ['department_name']

class AgendaAdmin(admin.ModelAdmin):
    list_display = ('agenda_date', 'agenda_title', 'department', 'get_agency')
    list_filter = ['agenda_date']

    def get_queryset(self, request):
        # Joins department and agency to query
        return super(AgendaAdmin,self).get_queryset(request).select_related('department__agency')

    def get_agency(self, obj):
        return obj.department.agency
    get_agency.admin_order_field =  'department__agency_name' #Allows column order sorting
    get_agency.short_description = 'Agency'  #Renames column heading

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "department":
            return DepartmentChoiceField(queryset=Department.objects.all())
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class DepartmentChoiceField(ModelChoiceField):
    # Override default ModelChoiceField to add Agency to Department label
    # This prevents confusion when multiple Agencies have same Department names
     def label_from_instance(self, obj):
         return "{} ({})".format(obj, obj.agency)

class CrawlerAdmin(admin.ModelAdmin):
    list_display = ('crawler_name', 'department', 'date_added')
    list_filter = ['date_added']
    search_fields = ['crawler_name']

admin.site.register(Agency, AgencyAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Agenda, AgendaAdmin)