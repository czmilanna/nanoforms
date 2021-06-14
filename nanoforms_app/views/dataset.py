import os
import uuid

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.views import generic

from nanoforms.settings import BASE_UPLOAD_DIR
from nanoforms_app.convert import unpack_tars, gzip_fastq, remove_files_with_extension_other_than_fastq_gz, sizeof_fmt, \
    unpack_zips
from nanoforms_app.mixin import OwnerAccessMixin, OwnerOrAdminOrPublicAccessMixin
from nanoforms_app.models import Dataset


def get_dataset_filter(request, id=None):
    dataset_filter = Dataset.objects.filter(Q(user=request.user) | Q(public=True)).order_by('created_at')
    if id:
        return dataset_filter.filter(id=id).first()
    else:
        return dataset_filter


def get_ref_dataset_filter(request, id=None):
    dataset_filter = Dataset.objects.filter(
        Q(user=request.user) | Q(public=True) | Q(type=Dataset.DatasetType.NANOPORE)).order_by('created_at')
    if id:
        return dataset_filter.filter(id=id).first()
    else:
        return dataset_filter


class DatasetListView(generic.ListView):
    model = Dataset

    def get_queryset(self):
        return get_dataset_filter(self.request)


class DatasetDetailView(OwnerOrAdminOrPublicAccessMixin, generic.DetailView):
    model = Dataset


class DatasetCreateForm(forms.ModelForm):
    class Meta:
        model = Dataset
        fields = ['name', 'type']

    files = forms.FileField(required=True,
                            widget=forms.ClearableFileInput(attrs={'multiple': True,
                                                                   'accept': '.fastq,.fastq.gz,.tar,.tar.gz,.zip'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'upload_form'
        self.helper.form_method = 'post'
        self.helper.form_action = 'dataset_create'
        self.helper.add_input(Submit('submit', 'Submit'))


class DatasetCreateView(generic.FormView):
    form_class = DatasetCreateForm
    template_name = 'nanoforms_app/dataset_create.html'

    def form_valid(self, form):
        files = self.request.FILES.getlist('files')
        username = self.request.user.username
        storage_id = str(uuid.uuid4())
        directory = f'{BASE_UPLOAD_DIR}{username}/{storage_id}/'
        os.makedirs(directory)

        for file in files:
            file_path = directory + file.name
            with open(file_path, 'wb+') as f:
                for chunk in file.chunks():
                    f.write(chunk)

        unpack_zips(directory)
        unpack_tars(directory, True)
        unpack_tars(directory, False)
        gzip_fastq(directory)
        remove_files_with_extension_other_than_fastq_gz(directory)

        all_files = [os.path.join(directory, f) for f in os.listdir(directory)]
        all_size = sum(os.path.getsize(f) for f in all_files)

        ds = Dataset(id=storage_id,
                     user_id=self.request.user.id,
                     directory=directory,
                     name=form.data['name'],
                     number_of_files=len(all_files),
                     size=sizeof_fmt(all_size),
                     type=form.data['type']
                     )
        ds.save()
        return JsonResponse({'id': ds.id})


class DeleteDatasetView(OwnerAccessMixin, generic.DeleteView):
    model = Dataset

    def get_success_url(self):
        return self.request.GET.get('next', reverse('index'))


def file_options(request, dataset_id, select_idx: int):
    dataset = get_dataset_filter(request).get(id=dataset_id)

    html = ''
    files = dataset.files()
    if len(files) < 2:
        select_idx = 0
    for idx, file in enumerate(files):
        file_name = file['name']
        html += f'<option value="{file_name}" {"selected" if idx == select_idx else ""}>{file_name}</td>'

    return HttpResponse(mark_safe(html))
