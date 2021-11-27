from wsgiref.util import FileWrapper

from django.http import HttpResponseForbidden, FileResponse

from nanoforms_app.cromwell import workflow_outputs
import mimetypes


def download(request, workflow_id, output_key, file_name):
    outputs = workflow_outputs(workflow_id).get('outputs', {})
    out = outputs.get(output_key)
    if isinstance(out, str):
        path = out
    else:
        path = next(x for x in out if x.endswith(file_name))
    if not path:
        return HttpResponseForbidden()

    response = FileResponse(FileWrapper(open(path, 'rb')))
    content_type, encoding = mimetypes.guess_type(file_name)
    response['Content-Type'] = content_type or 'application/octet-stream'
    # response['Content-Disposition'] = f'attachment; filename={file_name}'
    return response
