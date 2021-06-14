import json
from io import BytesIO
from time import sleep
from typing import List

import requests

from nanoforms.settings import CROMWELL_URL, WDL_DIR

_headers = {
    'accept': 'application/json'
}

_MAX_ATTEMPTS = 5


def workflow_quality_run(params: dict):
    return workflow_run(WDL_DIR.joinpath('basic').joinpath('prepare_data').joinpath('prepare_data.wdl'), params)

def workflow_illumina_quality_run(params: dict):
    return workflow_run(WDL_DIR.joinpath('basic').joinpath('prepare_illumina_data').joinpath('prepare_illumina_data.wdl'), params)


def workflow_data_assembly(params: dict):
    return workflow_run(WDL_DIR.joinpath('basic').joinpath('data_assembly').joinpath('data_assembly.wdl'), params)


def workflow_hybrid_assembly(params: dict):
    return workflow_run(WDL_DIR.joinpath('basic').joinpath('hybrid_assembly').joinpath('hybrid_assembly.wdl'), params)


def workflow_run(wdl_path: str, wdl_params: dict):
    json_bytes = BytesIO()
    json_bytes.write(json.dumps(wdl_params).encode())
    json_bytes.seek(0)
    files = {
        'workflowSource': ('a.wdl', open(wdl_path, 'rb')),
        'workflowInputs': ('a.json', json_bytes),
    }
    r = requests.post(f'{CROMWELL_URL}/api/workflows/v1',
                      headers=_headers, files=files)
    return r.json()


def workflow_metadata(workflow_id, attempt=0, query=''):
    r = requests.get(
        f'{CROMWELL_URL}/api/workflows/v1/{workflow_id}/metadata{"?" + query if query else ""}',
        headers=_headers)
    if r.status_code != 200 and attempt < _MAX_ATTEMPTS:
        sleep(1)
        return workflow_metadata(workflow_id, attempt + 1, query)
    return r.json()


def workflow_jobs(metadata) -> List[str]:
    lines = metadata.get('submittedFiles').get('workflow').split('\n')
    jobs = []
    for line in lines:
        line = str(line).strip()
        if 'call ' in line:
            job = line.split(' ')[1]
            jobs.append('call-' + job)
    return jobs


def workflow_outputs(workflow_id, attempt=0):
    r = requests.get(
        f'{CROMWELL_URL}/api/workflows/v1/{workflow_id}/outputs',
        headers=_headers)
    if r.status_code != 200 and attempt < _MAX_ATTEMPTS:
        sleep(1)
        return workflow_outputs(workflow_id, attempt + 1)
    return r.json()


def workflow_timing(workflow_id, attempt=0):
    r = requests.get(
        f'{CROMWELL_URL}/api/workflows/v1/{workflow_id}/timing')
    if r.status_code != 200 in r.text and attempt < _MAX_ATTEMPTS:
        sleep(1)
        return workflow_timing(workflow_id, attempt + 1)
    return r.text


def workflow_status(workflow_id, attempt=0):
    r = requests.get(
        f'{CROMWELL_URL}/api/workflows/v1/{workflow_id}/status',
        headers=_headers)
    if r.status_code != 200 and attempt < _MAX_ATTEMPTS:
        sleep(1)
        return workflow_status(workflow_id, attempt + 1)
    return r.json()['status']


def workflow_abort(workflow_id, attempt=0):
    r = requests.post(
        f'{CROMWELL_URL}/api/workflows/v1/{workflow_id}/abort',
        headers=_headers)
    if r.status_code != 200 and attempt < _MAX_ATTEMPTS:
        sleep(1)
        return workflow_status(workflow_id, attempt + 1)
    return r.json()['status']
