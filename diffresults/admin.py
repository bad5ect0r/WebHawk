from django import forms
from django.contrib import admin, messages
from django.urls import path, reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

from urllib.parse import urlparse

from . import models


class UrlImportForm(forms.Form):
    uploaded_file = forms.FileField()

    def __init__(self, *args, **kwargs):
        super(UrlImportForm, self).__init__(*args, **kwargs)
        self.fields['project'] = forms.ChoiceField(
            choices=[(m.id, m.project_name) for m in models.Project.objects.all()]
        )


class UrlProjectInline(admin.StackedInline):
    model = models.Url
    fields = ('url_name', 'full_url')
    extra = 1


class ProjectAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['project_name']}),
    ]
    inlines = [UrlProjectInline]


class HeaderUrlInline(admin.TabularInline):
    model = models.Header
    extra = 3


class UrlAdmin(admin.ModelAdmin):
    change_list_template = 'admin/change_list/urls.html'
    list_display = ('url_name', 'method', 'full_url', 'add_date', 'last_fetched_date', 'project')
    inlines = [HeaderUrlInline]

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import', self.file_import, name='import')
        ]
        return my_urls + urls

    def file_import(self, request):
        if (request.method == 'POST' and
            'uploaded_file' in request.FILES and
            'project' in request.POST):
            uploaded_file = request.FILES['uploaded_file']
            project = get_object_or_404(models.Project, pk=int(request.POST['project']))
            bad_line_urls = project.import_urls_from_file(uploaded_file)

            if len(bad_line_urls) > 0:
                return render(request,
                    'admin/url_import_fail.html',
                    {
                        'bad_line_urls': bad_line_urls,
                    },
                    status=400
                )
            else:
                return HttpResponseRedirect(reverse('admin:diffresults_url_changelist'))
        else:
            if len(models.Project.objects.all()) > 0:
                form = UrlImportForm()
                return render(request, 'admin/url_import.html', {'form': form})
            else:
                self.message_user(
                    request,
                    'You must create a project first.',
                    messages.ERROR
                )
                return HttpResponseRedirect(reverse('admin:diffresults_project_add'))


admin.site.register(models.Project, ProjectAdmin)
admin.site.register(models.Url, UrlAdmin)
admin.site.site_header = 'WebHawk Admin'
admin.site.site_title = 'WebHawk Admin'

