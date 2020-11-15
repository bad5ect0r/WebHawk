from django.urls import path

from . import views

app_name = 'diffresults'
urlpatterns = [
    path('', views.index, name='index'),
    path('project/<int:project_id>', views.project, name='project'),
    path('fetch/<int:url_id>', views.fetch, name='fetch')
]
