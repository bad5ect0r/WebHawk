from django.urls import path

from . import views

app_name = 'diffresults'
urlpatterns = [
    path('', views.MainDashboard.as_view(), name='main'),
    path('project/<int:pk>', views.ProjectDashboard.as_view(), name='project'),
    path('fetch/<int:pk>', views.fetch, name='fetch'),
    path('url/<int:pk>', views.UrlDashboard.as_view(), name='url'),
    path('url/<int:pk>/<str:commit_a>/<str:commit_b>', views.UrlDashboard.as_view(), name='url-with-args')
]
