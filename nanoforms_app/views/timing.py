from django.http import HttpResponse
from django.utils.safestring import mark_safe

from nanoforms_app.cromwell import workflow_timing
from nanoforms_app.models import Workflow


def timing(request, workflow_id):
    workflow = Workflow.objects.get(id=workflow_id)
    if not workflow.submitted:
        html = workflow_timing(workflow.id)
        html = html.replace('./metadata', f'/metadata/{workflow.id}')
        html = html.replace('prz_prepare_data.', '')
        html = html.replace('prz_prepare_illumina_data.', '')
        html = html.replace('prz_data_assembly.', '')
        html = html.replace('prz_hybrid_assembly.', '')
        response = mark_safe(html)
    else:
        response = mark_safe('<span>Waiting for workflow to start. ' +
                             'With high activity on the server, your workflow may wait in the queue for some time.'
                             + '</span>')
    return HttpResponse(response)
