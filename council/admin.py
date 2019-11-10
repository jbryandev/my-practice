from django.contrib import admin

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

admin.site.register(Agency, AgencyAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Agenda, AgendaAdmin)