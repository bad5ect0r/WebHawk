from django.urls import path

from . import views

app_name = 'diffresults'
urlpatterns = [
    path('', views.MainDashboard.as_view(), name='main'),
    path('project/<int:pk>', views.ProjectDashboard.as_view(), name='project'),
    path('fetch/<int:pk>', views.fetch, name='fetch')
]
