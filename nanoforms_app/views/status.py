from django.http import HttpResponse
from django.utils.safestring import mark_safe

from nanoforms_app.cromwell import workflow_metadata
from nanoforms_app.models import Workflow


def status(request, workflow_id):
    workflow = Workflow.objects.get(id=workflow_id)
    metadata = workflow_metadata(workflow_id)
    cromwell_status = metadata['status']
    if workflow.status != cromwell_status:
        workflow.status = cromwell_status
        workflow.save()
        if workflow.processed:
            from nanoforms_app.cromwell_events import CromwellEvents
            CromwellEvents.workflow_ended(workflow)
        response = '<script>location.reload();</script>'
    elif workflow.running or workflow.submitted:
        response = 'You will receive an e-mail notification when the calculations are completed.'
    else:
        response = ''
    return HttpResponse(mark_safe(response))
