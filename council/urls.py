from django.urls import path

from . import views

app_name = 'council'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/', views.AgencyView.as_view(), name='agency-detail'),
    path('departments/<int:pk>/', views.DepartmentView.as_view(), name='department-detail'),
]
