import glob
import mimetypes
import os
import zipfile
from wsgiref.util import FileWrapper
from zipfile import ZipFile

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.http import HttpResponseRedirect, Http404, FileResponse
from django.urls import reverse
from django.views import generic

from nanoforms_app.cromwell import workflow_hybrid_assembly
from nanoforms_app.mixin import OwnerOrAdminOrPublicAccessMixin
from nanoforms_app.models import Workflow, Dataset
from nanoforms_app.views.dataset import get_dataset_filter

READ_INITIAL_CHOICES = [(None, 'Select Illumina dataset to display choices')]


class ChoiceFieldNoValidation(forms.ChoiceField):
    def valid_value(self, value):
        return True


class HybridAssemblyCreateForm(forms.ModelForm):
    class Meta:
        model = Workflow
        fields = ['name', 'dataset', 'secondary_dataset', 'parent']
        widgets = {'parent': forms.HiddenInput()}

    illumina_read1 = ChoiceFieldNoValidation(choices=READ_INITIAL_CHOICES)
    illumina_read2 = ChoiceFieldNoValidation(choices=READ_INITIAL_CHOICES)
    nanofilt_q = forms.IntegerField(initial=5)
    nanofilt_headcrop = forms.IntegerField(initial=0)
    fastp_q = forms.IntegerField(initial=10)
    prokka_genus = forms.CharField(initial="Genus", required=False)
    prokka_species = forms.CharField(initial="species", required=False)
    prokka_strain = forms.CharField(initial="strain", required=False)
    prokka_plasmid = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['parent'].label = 'Quality'
        self.fields['parent'].required = False
        self.fields['dataset'].label = 'Nanopore dataset'
        self.fields['secondary_dataset'].label = 'Illumina dataset'
        self.fields['nanofilt_q'].label = """<h6>These parameters are optional or default, but you can change them if you want:</h6><br/>
                <span data-toggle="tooltip" style="cursor: pointer" data-placement="top" 
                title="filter on a minimum average read quality score (for example, 10)">Nanopore Nanofilt -q <span class="info"></span></span>"""
        self.fields['nanofilt_headcrop'].label = """<span data-toggle="tooltip" style="cursor: pointer" data-placement="top" 
                        title="trim nucleotides from start of read (for example, 75)">Nanopore Nanofilt -headcrop <span class="info"></span></span>"""
        self.fields['fastp_q'].label = """<span data-toggle="tooltip" style="cursor: pointer" data-placement="top" 
                title="the quality value that a base is qualified (for example, 15)">Illumina fastp -q <span class="info"></span></span>"""
        self.fields['prokka_genus'].label = """<span data-toggle="tooltip" style="cursor: pointer" data-placement="top" 
                title="genus name (for example, Genus)">Prokka --genus<span class="info"></span></span>"""
        self.fields['prokka_species'].label = """<span data-toggle="tooltip" style="cursor: pointer" data-placement="top" 
                title="species name (for example, species)">Prokka --species<span class="info"></span></span>"""
        self.fields['prokka_strain'].label = """<span data-toggle="tooltip" style="cursor: pointer" data-placement="top" 
                title="strain name (for example, strain)">Prokka --strain<span class="info"></span></span>"""
        self.fields['prokka_plasmid'].label = """<span data-toggle="tooltip" style="cursor: pointer" data-placement="top" 
                title="plasmid name (for example, plasmid)">Prokka --plasmid<span class="info"></span></span>"""
        self.helper = FormHelper()
        self.helper.form_id = 'hybrid_create'
        self.helper.form_method = 'post'
        self.helper.form_action = 'hybrid_create'
        self.helper.add_input(Submit('submit', 'Submit'))


class HybridAssemblyCreateView(generic.FormView):
    form_class = HybridAssemblyCreateForm
    template_name = 'nanoforms_app/hybrid_create.html'

    def get_form(self, form_class=None):
        args = self.get_form_kwargs()
        if self.request.GET:
            quality_id = self.request.GET.get('quality_id')
            if quality_id:
                quality = Workflow.objects.get(pk=quality_id)
            else:
                quality = Workflow.objects.get(pk=args.get('data').get('parent'))

            ds_field = 'dataset' if quality.dataset.type == Dataset.DatasetType.NANOPORE else 'secondary_dataset'
            args.update({'initial': {'parent': quality, ds_field: quality.dataset}})

        form = HybridAssemblyCreateView.form_class(**args)

        form.fields['dataset'].queryset = get_dataset_filter(self.request).filter(type=Dataset.DatasetType.NANOPORE)
        form.fields['secondary_dataset'].queryset = get_dataset_filter(self.request).filter(
            type=Dataset.DatasetType.ILLUMINA)
        return form

    def form_valid(self, form):
        workflow = form.instance
        prokka_genus = form.data['prokka_genus']
        prokka_species = form.data['prokka_species']
        prokka_strain = form.data['prokka_strain']
        prokka_plasmid = form.data['prokka_plasmid']
        if prokka_genus:
            prokka_genus = ''.join(str(prokka_genus).split())
        if prokka_species:
            prokka_species = ''.join(str(prokka_species).split())
        if prokka_strain:
            prokka_strain = ''.join(str(prokka_strain).split())
        if prokka_plasmid:
            prokka_plasmid = ''.join(str(prokka_plasmid).split())
        params = {
            'prz_hybrid_assembly.nanopore_directory': workflow.dataset.directory,
            'prz_hybrid_assembly.kraken_db': "/Q/data/prz/minikraken2_v2_8GB_201904_UPDATE/",
            'prz_hybrid_assembly.nanofilt.nanopore_headcrop': int(form.data['nanofilt_headcrop']),
            'prz_hybrid_assembly.nanofilt.nanopore_q': int(form.data['nanofilt_q']),
            'prz_hybrid_assembly.fastp.illumina_q': int(form.data['fastp_q']),
            "prz_hybrid_assembly.illumina_read1": workflow.secondary_dataset.directory + form.data['illumina_read1'],
            "prz_hybrid_assembly.illumina_read2": workflow.secondary_dataset.directory + form.data['illumina_read2'],
            'prz_hybrid_assembly.prokka.genus': f" --genus {prokka_genus} " if prokka_genus else ' ',
            'prz_hybrid_assembly.prokka.species': f" --species {prokka_species} " if prokka_species else ' ',
            'prz_hybrid_assembly.prokka.strain': f" --strain {prokka_strain} " if prokka_strain else ' ',
            'prz_hybrid_assembly.prokka.plasmid': f" --plasmid {prokka_plasmid} " if prokka_plasmid else ' '
        }
        print(params)
        run = workflow_hybrid_assembly(params)
        workflow.id = run['id']
        workflow.user = self.request.user
        workflow.type = Workflow.WorkflowType.HYBRID
        workflow.save()
        return HttpResponseRedirect(reverse('hybrid_detail', kwargs={'pk': workflow.id}))


class HybridAssemblyDetailView(OwnerOrAdminOrPublicAccessMixin, generic.DetailView):
    model = Workflow
    template_name = 'nanoforms_app/hybrid_detail.html'


def add_folder_to_zip(myZipFile, folder, prefix=''):
    if folder:
        for file in glob.glob(folder + "/*"):
            next_folder = os.path.join(prefix, os.path.basename(file))
            if os.path.isfile(file):
                myZipFile.write(file, next_folder, zipfile.ZIP_DEFLATED)
            elif os.path.isdir(file):
                add_folder_to_zip(myZipFile, file, next_folder)


def download_hybrid_report(request, workflow_id):
    workflow = Workflow.objects.get(id=workflow_id)
    o = workflow.output.get('outputs')
    if not o:
        return Http404
    file_name = f'report-{workflow_id}.zip'

    zipfile = ZipFile(file_name, mode='a')
    zipfile.write(o.get('prz_hybrid_assembly.krona_report'), 'taxon-visual/kraken2_krona_report.html')
    zipfile.write(o.get('prz_hybrid_assembly.kraken2_report'), 'taxon-visual/kraken2_report')
    zipfile.write(o.get('prz_hybrid_assembly.consensus'), 'assembly.fasta')
    zipfile.write(o.get('prz_hybrid_assembly.assembly_image'), 'assembly-image-bandage/assembly_image.jpg')
    zipfile.write(o.get('prz_hybrid_assembly.unicycler_graph'), 'assembly-image-bandage/consensus.gfa')
    add_folder_to_zip(zipfile, o.get('prz_hybrid_assembly.quast_logs'), 'assembly-evaluation-quast/')
    add_folder_to_zip(zipfile, o.get('prz_hybrid_assembly.prokka_logs'), 'genome-annotation-prokka/')
    response = FileResponse(FileWrapper(open(file_name, 'rb')))
    content_type, encoding = mimetypes.guess_type(file_name)
    response['Content-Type'] = content_type or 'application/octet-stream'
    os.remove(file_name)
    return response
