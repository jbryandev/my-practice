from council.tasks import fetch_agendas
from council.models import Department

print("---RUNNING FETCH AGENDAS NIGHTLY TASK---")
departments = Department.objects.all()
for department in departments:
        print("Fetching agendas for {} - {}".format(department.agency, department.department_name))
        #fetch_agendas.delay(department.id)