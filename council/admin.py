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
    list_display = ('agenda_date', 'department', 'date_added')
    list_filter = ['agenda_date']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "department":
            #kwargs["queryset"] = Department.objects.all()
            #for department in kwargs["queryset"]:
            #    department.department_name += (" (" + str(Agency.objects.get(id=department.agency_id)) + ")")
            #print(kwargs["queryset"])
            return DepartmentChoiceField(queryset=Department.objects.all())
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class DepartmentChoiceField(ModelChoiceField):
    # Override default ModelChoiceField to add Agency to Department label
    # This prevents confusion when multiple Agencies have same Department names
     def label_from_instance(self, obj):
         return "{} ({})".format(obj, obj.agency)

admin.site.register(Agency, AgencyAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Agenda, AgendaAdmin)