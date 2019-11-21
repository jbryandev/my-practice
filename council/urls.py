from django.urls import path

from . import views

app_name = 'council'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/', views.AgencyView.as_view(), name='agency-detail'),
    path('department/<int:pk>/', views.DepartmentView.as_view(), name='department-detail'),
    path('agenda/<int:pk>/', views.AgendaView.as_view(), name='agenda-detail'),
    path('department/<int:pk>/fetch', views.fetch_agendas, name='fetch-agendas'),
]
