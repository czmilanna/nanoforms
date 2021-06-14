import os

from django.http import HttpResponse
from django.utils import timezone
from django.utils.formats import date_format
from django.utils.safestring import mark_safe

from nanoforms_app.models import Workflow


def metadata(request, workflow_id):
    workflow = Workflow.objects.get(id=workflow_id)
    inputs = workflow.metadata.get('inputs')
    for k, v in inputs.items():
        print(k, v)

    html = ''
    html += f'<td>{workflow.status}</td>'
    html += f'<td>{workflow.dataset.name}</td>'
    html += f'<td>{workflow.parent.name if workflow.parent else "Not performed"}</td>'
    result = timezone.localtime(workflow.created_at, timezone.get_current_timezone())
    html += f'<td>{date_format(result, "DATETIME_FORMAT")}</td>'
    # html += f'<td>{inputs.get("prz_data_assembly.nanofilt.q", "")}</td>'
    # html += f'<td>{inputs.get("prz_data_assembly.nanofilt.headcrop", "")}</td>'

    return HttpResponse(mark_safe(html))

def assembly_details(request, workflow_id):
    workflow = Workflow.objects.get(id=workflow_id)
    inputs = workflow.metadata.get('inputs')

    prokka_genus = inputs.get("prz_data_assembly.prokka.genus", "").split()
    if len(prokka_genus) > 1:
        prokka_genus = prokka_genus[1]
    else:
        prokka_genus = "-"

    prokka_species = inputs.get("prz_data_assembly.prokka.species", "").split()
    if len(prokka_species) > 1:
        prokka_species = prokka_species[1]
    else:
        prokka_species = "-"

    prokka_strain = inputs.get("prz_data_assembly.prokka.strain", "").split()
    if len(prokka_strain) > 1:
        prokka_strain = prokka_strain[1]
    else:
        prokka_strain = "-"

    prokka_plasmid = inputs.get("prz_data_assembly.prokka.plasmid", "").split()
    if len(prokka_plasmid) > 1:
        prokka_plasmid = prokka_plasmid[1]
    else:
        prokka_plasmid = "-"

    flye_g = inputs.get("prz_data_assembly.flye.g", "").split()
    if len(flye_g) > 1:
        flye_g = flye_g[1]
    else:
        flye_g = "-"

    html = ''
    html += f'<td>{inputs.get("prz_data_assembly.nanofilt.q", "")}</td>'
    html += f'<td>{inputs.get("prz_data_assembly.nanofilt.headcrop", "")}</td>'
    html += f'<td>{inputs.get("prz_data_assembly.filtlong.min_length", "")}</td>'
    html += f'<td>{inputs.get("prz_data_assembly.filtlong.target_bases", "")}</td>'
    html += f'<td>{prokka_genus}</td>'
    html += f'<td>{prokka_species}</td>'
    html += f'<td>{prokka_strain}</td>'
    html += f'<td>{prokka_plasmid}</td>'
    html += f'<td>{flye_g}</td>'

    return HttpResponse(mark_safe(html))


def hybrid_metadata(request, workflow_id):
    workflow = Workflow.objects.get(id=workflow_id)
    inputs = workflow.metadata.get('inputs')
    for k, v in inputs.items():
        print(k, v)

    html = ''
    html += f'<td>{workflow.status}</td>'
    html += f'<td>{workflow.dataset.name}</td>'
    r1 = os.path.basename(inputs.get('prz_hybrid_assembly.illumina_read1', ''))
    r2 = os.path.basename(inputs.get('prz_hybrid_assembly.illumina_read2', ''))
    html += f'<td>{r1},{r2}</td>'
    html += f'<td>{workflow.parent.name if workflow.parent else "Not performed"}</td>'
    result = timezone.localtime(workflow.created_at, timezone.get_current_timezone())
    html += f'<td>{date_format(result, "DATETIME_FORMAT")}</td>'
    return HttpResponse(mark_safe(html))

def hybrid_details(request, workflow_id):
    workflow = Workflow.objects.get(id=workflow_id)
    inputs = workflow.metadata.get('inputs')

    prokka_genus = inputs.get("prz_hybrid_assembly.prokka.genus", "").split()
    if len(prokka_genus) > 1:
        prokka_genus = prokka_genus[1]
    else:
        prokka_genus = "-"

    prokka_species = inputs.get("prz_hybrid_assembly.prokka.species", "").split()
    if len(prokka_species) > 1:
        prokka_species = prokka_species[1]
    else:
        prokka_species = "-"

    prokka_strain = inputs.get("prz_hybrid_assembly.prokka.strain", "").split()
    if len(prokka_strain) > 1:
        prokka_strain = prokka_strain[1]
    else:
        prokka_strain = "-"

    prokka_plasmid = inputs.get("prz_hybrid_assembly.prokka.plasmid", "").split()
    if len(prokka_plasmid) > 1:
        prokka_plasmid = prokka_plasmid[1]
    else:
        prokka_plasmid = "-"

    html = ''
    html += f'<td>{inputs.get("prz_hybrid_assembly.nanofilt.nanopore_q", "")}</td>'
    html += f'<td>{inputs.get("prz_hybrid_assembly.nanofilt.nanopore_headcrop", "")}</td>'
    html += f'<td>{inputs.get("prz_hybrid_assembly.fastp.illumina_q", "")}</td>'
    html += f'<td>{prokka_genus}</td>'
    html += f'<td>{prokka_species}</td>'
    html += f'<td>{prokka_strain}</td>'
    html += f'<td>{prokka_plasmid}</td>'

    return HttpResponse(mark_safe(html))
