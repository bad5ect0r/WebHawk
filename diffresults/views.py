from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views import generic
from django.http import Http404

from . import models


class MainDashboard(generic.ListView):
    template_name = 'diffresults/index.html'
    context_object_name = 'projects'

    def get_queryset(self):
        return models.Project.objects.all()


class ProjectDashboard(generic.DetailView):
    model = models.Project
    context_object_name = 'project'
    template_name = 'diffresults/project.html'


class UrlDashboard(generic.DetailView):
    model = models.Url

    def get(self, request, pk, commit_a=None, commit_b=None):
        url = get_object_or_404(self.model, pk=pk)
        commits = url.get_commits()
        diff = ''

        if len(commits) > 1:
            if commit_a is None or commit_b is None:
                diff = url.get_diff(commits[1], commits[0])
            else:
                commit_a = url.get_commit_from_sha(commit_a)
                commit_b = url.get_commit_from_sha(commit_b)

                if commit_a is not None and commit_b is not None:
                    diff = url.get_diff(commit_a, commit_b)
                else:
                    raise Http404('Invalid commit hashes.')

        return render(request, 'diffresults/url.html', {
            'url': url,
            'commits': commits,
            'diff': diff
        })

    def post(self, request, pk, commit_a=None, commit_b=None):
        if 'before' in request.POST and 'after' in request.POST:
            args = {
                'pk': pk,
                'commit_a': request.POST['before'],
                'commit_b': request.POST['after']
            }
            return redirect(reverse('diffresults:url-with-args', kwargs=args))
        else:
            return redirect(reverse('diffresults:url', args=[pk]))


def fetch(request, pk):
    url = get_object_or_404(models.Url, pk=pk)
    resp = url.fetch()

    return render(request, 'diffresults/fetch.html', {
        'full_request': resp.request,
        'response_text': resp.text
    })
