import mimetypes
import os
import zipfile
from wsgiref.util import FileWrapper
from zipfile import ZipFile
import glob

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.db.models import Q
from django.http import FileResponse, Http404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic

from nanoforms_app.cromwell import workflow_data_assembly
from nanoforms_app.mixin import OwnerOrAdminOrPublicAccessMixin
from nanoforms_app.models import Workflow, Dataset
from nanoforms_app.views.dataset import get_dataset_filter


class AssemblyListView(generic.ListView):
    model = Workflow
    template_name = 'nanoforms_app/assembly_list.html'

    def get_queryset(self):
        queryset = super(AssemblyListView, self).get_queryset()
        queryset = queryset.filter(Q(user=self.request.user) | Q(public=True)).filter(
            Q(type=Workflow.WorkflowType.ASSEMBLY) | Q(type=Workflow.WorkflowType.HYBRID)).order_by('created_at')
        return queryset


class AssemblyCreateForm(forms.ModelForm):
    class Meta:
        model = Workflow
        fields = ['name', 'dataset', 'parent']
        widgets = {'parent': forms.HiddenInput()}

    flye_g = forms.CharField(required=False)
    nanofilt_q = forms.IntegerField(initial=5)
    nanofilt_headcrop = forms.IntegerField(initial=0)
    filtlong_min_length = forms.IntegerField(initial=1000)
    filtlong_target_bases = forms.IntegerField(initial=500000000)
    prokka_genus = forms.CharField(initial="Genus", required=False)
    prokka_species = forms.CharField(initial="species", required=False)
    prokka_strain = forms.CharField(initial="strain", required=False)
    prokka_plasmid = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['parent'].label = 'Quality'
        self.fields['parent'].required = False
        self.fields['flye_g'].label = """<h6>These parameters are optional or default, but you can change them if you want:</h6>
                <br/><span data-toggle="tooltip" style="cursor: pointer" data-placement="top"
                title="estimated genome size (for example, 5m or 2.6g)">Flye -g<span class="info"></span> </span>"""
        self.fields['nanofilt_q'].label = """<span data-toggle="tooltip" style="cursor: pointer" data-placement="top" 
                title="filter on a minimum average read quality score (for example, 10)">Nanofilt -q <span class="info"></span></span>"""
        self.fields['nanofilt_headcrop'].label = """<span data-toggle="tooltip" style="cursor: pointer" data-placement="top" 
                title="trim nucleotides from start of read (for example, 75)">Nanofilt -headcrop <span class="info"></span></span>"""
        self.fields['filtlong_min_length'].label = """<span data-toggle="tooltip" style="cursor: pointer" data-placement="top"
                title="keep only this percentage of the best reads measured by bases (for example, 1000 - discard any read which is shorter than 1 kbp)">
                Filtlong --min_length <span class="info"></span></span>"""
        self.fields['filtlong_target_bases'].label = """<span data-toggle="tooltip" style="cursor: pointer" data-placement="top"
                 title="keep only the best reads up to this many total bases (for example, 500000000 - remove the worst reads until only 500 Mbp remain, useful for very large read sets. If the input read set is less than 500 Mbp, this setting will have no effect)">Filtlong --target_bases<span class="info"></span></span>"""
        self.fields['prokka_genus'].label = """<span data-toggle="tooltip" style="cursor: pointer" data-placement="top" 
                title="genus name (for example, Genus)">Prokka --genus<span class="info"></span></span>"""
        self.fields['prokka_species'].label = """<span data-toggle="tooltip" style="cursor: pointer" data-placement="top" 
                title="species name (for example, species)">Prokka --species<span class="info"></span></span>"""
        self.fields['prokka_strain'].label = """<span data-toggle="tooltip" style="cursor: pointer" data-placement="top" 
                title="strain name (for example, strain)">Prokka --strain<span class="info"></span></span>"""
        self.fields['prokka_plasmid'].label = """<span data-toggle="tooltip" style="cursor: pointer" data-placement="top" 
                title="plasmid name or identifier (for example, plasmid)">Prokka --plasmid<span class="info"></span></span>"""
        self.helper = FormHelper()
        self.helper.form_id = 'assembly_create'
        self.helper.form_method = 'post'
        self.helper.form_action = 'assembly_create'
        self.helper.add_input(Submit('submit', 'Submit'))


class AssemblyCreateView(generic.FormView):
    form_class = AssemblyCreateForm
    template_name = 'nanoforms_app/assembly_create.html'

    def get_form(self, form_class=None):
        args = self.get_form_kwargs()
        if self.request.GET:
            quality_id = self.request.GET.get('quality_id')
            if quality_id:
                quality = Workflow.objects.get(pk=quality_id)
                args.update({'initial': {'dataset': quality.dataset, 'parent': quality}})
            else:
                quality = Workflow.objects.get(pk=args.get('data').get('parent'))
                args.update({'initial': {'dataset': quality.dataset, 'parent': quality}})

        form = AssemblyCreateView.form_class(**args)
        form.fields['dataset'].queryset = get_dataset_filter(self.request).filter(type=Dataset.DatasetType.NANOPORE)
        return form

    def form_valid(self, form):
        workflow = form.instance
        flye_g = form.data['flye_g']
        prokka_genus = form.data['prokka_genus']
        prokka_species = form.data['prokka_species']
        prokka_strain = form.data['prokka_strain']
        prokka_plasmid = form.data['prokka_plasmid']

        if flye_g:
            flye_g = ''.join(str(flye_g).split())  # remove whitespaces
        if prokka_genus:
            prokka_genus = ''.join(str(prokka_genus).split())
        if prokka_species:
            prokka_species = ''.join(str(prokka_species).split())
        if prokka_strain:
            prokka_strain = ''.join(str(prokka_strain).split())
        if prokka_plasmid:
            prokka_plasmid = ''.join(str(prokka_plasmid).split())
        params = {
            'prz_data_assembly.nanofilt.q': int(form.data['nanofilt_q']),
            'prz_data_assembly.fastq_directory': workflow.dataset.directory,
            'prz_data_assembly.flye.g': f" -g {flye_g} " if flye_g else ' ',
            'prz_data_assembly.nanofilt.headcrop': int(form.data['nanofilt_headcrop']),
            'prz_data_assembly.filtlong.min_length': int(form.data['filtlong_min_length']),
            'prz_data_assembly.filtlong.target_bases': int(form.data['filtlong_target_bases']),
            'prz_data_assembly.prokka.genus':  f" --genus {prokka_genus} " if prokka_genus else ' ',
            'prz_data_assembly.prokka.species': f" --species {prokka_species} " if prokka_species else ' ',
            'prz_data_assembly.prokka.strain': f" --strain {prokka_strain} " if prokka_strain else ' ',
            'prz_data_assembly.prokka.plasmid': f" --plasmid {prokka_plasmid} " if prokka_plasmid else ' '
        }
        run = workflow_data_assembly(params)
        workflow.id = run['id']
        workflow.user = self.request.user
        workflow.type = Workflow.WorkflowType.ASSEMBLY
        workflow.save()
        return HttpResponseRedirect(reverse('assembly_detail', kwargs={'pk': workflow.id}))


class AssemblyDetailView(OwnerOrAdminOrPublicAccessMixin, generic.DetailView):
    model = Workflow
    template_name = 'nanoforms_app/assembly_detail.html'


def addFolderToZip(myZipFile, folder, prefix=''):
    for file in glob.glob(folder + "/*"):
        if os.path.isfile(file):
            myZipFile.write(file, prefix + os.path.basename(file), zipfile.ZIP_DEFLATED)
        elif os.path.isdir(file):
            addFolderToZip(myZipFile, file, prefix + os.path.basename(file))


def download_assembly_report(request, workflow_id):
    workflow = Workflow.objects.get(id=workflow_id)
    o = workflow.output.get('outputs')
    if not o:
        return Http404
    file_name = f'report-{workflow_id}.zip'

    zipfile = ZipFile(file_name, mode='a')
    zipfile.write(o.get('prz_data_assembly.assembly_image'), 'assembly-image-bandage/assembly_image.jpg')
    zipfile.write(o.get('prz_data_assembly.assembly_graph'), 'assembly-image-bandage/assembly_graph.gfa')
    zipfile.write(o.get('prz_data_assembly.consensus_fasta'), 'consensus-file/consensus.fasta')
    addFolderToZip(zipfile, o.get('prz_data_assembly.quast_logs'), 'assembly-evaluation-quast/')
    addFolderToZip(zipfile, o.get('prz_data_assembly.prokka_logs'), 'genome-annotation-prokka/')
    response = FileResponse(FileWrapper(open(file_name, 'rb')))
    content_type, encoding = mimetypes.guess_type(file_name)
    response['Content-Type'] = content_type or 'application/octet-stream'
    os.remove(file_name)
    return response
