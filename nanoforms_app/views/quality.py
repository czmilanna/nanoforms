import mimetypes
import os
from wsgiref.util import FileWrapper
from zipfile import ZipFile

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.db.models import Q
from django.http import HttpResponseRedirect, FileResponse, Http404
from django.urls import reverse
from django.views import generic

from nanoforms_app.cromwell import workflow_quality_run, workflow_illumina_quality_run
from nanoforms_app.mixin import OwnerOrAdminOrPublicAccessMixin
from nanoforms_app.models import Workflow, Dataset
from nanoforms_app.views.dataset import get_dataset_filter
from nanoforms_app.access import has_access_filter


class QualityListView(generic.ListView):
    model = Workflow
    template_name = 'nanoforms_app/quality_list.html'

    def get_queryset(self):
        queryset = super(QualityListView, self).get_queryset()
        queryset = queryset.filter(has_access_filter(self.request) | Q(public=True)).filter(
            type=Workflow.WorkflowType.QUALITY).order_by('created_at')
        return queryset


class QualityCreateForm(forms.ModelForm):
    class Meta:
        model = Workflow
        fields = ['name', 'dataset']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_action = 'quality_create'
        self.helper.add_input(Submit('submit', 'Submit'))


class QualityCreateView(generic.FormView):
    form_class = QualityCreateForm
    template_name = 'nanoforms_app/quality_create.html'

    def get_form(self, form_class=None):
        args = self.get_form_kwargs()
        dataset_id = self.request.GET.get('dataset_id')
        if dataset_id:
            args.update({'initial': {'dataset': get_dataset_filter(self.request, dataset_id)}})
        form = QualityCreateView.form_class(**args)
        form.fields['dataset'].queryset = get_dataset_filter(self.request)
        return form

    def form_valid(self, form):
        workflow = form.instance
        if workflow.dataset.type == Dataset.DatasetType.NANOPORE:
            run = workflow_quality_run({
                'prz_prepare_data.data_directory': workflow.dataset.directory
            })
        else:
            run = workflow_illumina_quality_run({
                'prz_prepare_illumina_data.data_directory': workflow.dataset.directory
            })
        workflow.id = run['id']
        workflow.user = self.request.user
        workflow.type = Workflow.WorkflowType.QUALITY
        workflow.save()
        return HttpResponseRedirect(reverse('quality_detail', kwargs={'pk': workflow.id}))


class QualityDetailView(OwnerOrAdminOrPublicAccessMixin, generic.DetailView):
    model = Workflow
    template_name = 'nanoforms_app/quality_detail.html'


def download_quality_report(request, workflow_id):
    workflow = Workflow.objects.get(id=workflow_id)
    o = workflow.output.get('outputs')
    if not o:
        return Http404
    file_name = f'report-{workflow_id}.zip'

    zipfile = ZipFile(file_name, mode='a')

    if workflow.dataset.type == Dataset.DatasetType.NANOPORE:
        zipfile.write(o.get('prz_prepare_data.stats'), 'NanoStats.txt')
        for p in o.get('prz_prepare_data.htmls'):
            zipfile.write(p, os.path.basename(p))
        for p in o.get('prz_prepare_data.images'):
            zipfile.write(p, os.path.basename(p))
    elif workflow.dataset.type == Dataset.DatasetType.ILLUMINA:
        v = o.get('prz_prepare_illumina_data.out_html')
        zipfile.write(v, os.path.basename(v))

    response = FileResponse(FileWrapper(open(file_name, 'rb')))
    content_type, encoding = mimetypes.guess_type(file_name)
    response['Content-Type'] = content_type or 'application/octet-stream'
    os.remove(file_name)
    return response
