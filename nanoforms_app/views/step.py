from django.http import HttpResponse
from django.utils.safestring import mark_safe

from nanoforms_app.cromwell import workflow_metadata, workflow_jobs


def step(request, workflow_id):
    try:
        metadata = workflow_metadata(workflow_id)
        jobs = workflow_jobs(metadata)
        calls = metadata['calls']
        response = f'Running step {len(calls)} out of {len(jobs)}'
    except:
        response = ''
    return HttpResponse(mark_safe(response))
