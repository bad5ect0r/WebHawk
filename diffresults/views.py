from django.shortcuts import render, get_object_or_404

from . import models


def index(request):
    projects = models.Project.objects.all()

    return render(request, 'diffresults/index.html', {
        'projects': projects
    })


def project(request, project_id):
    project = get_object_or_404(models.Project, pk=project_id)
    urls = project.url_set.all()

    return render(request, 'diffresults/project.html', {
        'project': project,
        'urls': urls
    })


def fetch(request, url_id):
    url = get_object_or_404(models.Url, pk=url_id)
    resp = url.fetch()

    return render(request, 'diffresults/fetch.html', {
        'full_request': resp.request,
        'response_text': resp.text
    })


