from django.shortcuts import render, get_object_or_404
from django.views import generic

from . import models


class MainDashboard(generic.ListView):
    template_name = 'diffresults/index.html'
    context_object_name = 'projects'

    def get_queryset(self):
        return models.Project.objects.all()


class ProjectDashboard(generic.DetailView):
    model = models.Project
    template_name = 'diffresults/project.html'


def fetch(request, pk):
    url = get_object_or_404(models.Url, pk=pk)
    resp = url.fetch()

    return render(request, 'diffresults/fetch.html', {
        'full_request': resp.request,
        'response_text': resp.text
    })
