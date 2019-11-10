from django.contrib import admin

from .models import Agency, Department

# Register your models here.

class AgencyAdmin(admin.ModelAdmin):
    list_display = ('agency_name', 'date_added')
    list_filter = ['date_added']
    search_fields = ['agency_name']

class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('department_name', 'agency', 'date_added')
    list_filter = ['date_added']
    search_fields = ['department_name']

admin.site.register(Agency, AgencyAdmin)
admin.site.register(Department, DepartmentAdmin)