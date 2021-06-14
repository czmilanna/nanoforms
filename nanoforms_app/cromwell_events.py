from pathlib import Path
from shutil import rmtree
from threading import Thread
from time import sleep

from nanoforms import settings
from nanoforms_app.models import Workflow


class CromwellEvents:

    @staticmethod
    def workflow_ended(workflow: Workflow):

        msg = f'{workflow.get_type_display()} workflow with name "{workflow.name}" finished with status "{workflow.status}".'
        print(msg)

        # notify user
        try:
            workflow.user.email_user('Nanoforms Status', msg, settings.DEFAULT_FROM_EMAIL)
        except:
            print('Can not sent email')

        # cleanup

        if workflow.aborted:
            workflow_root_dir = workflow.metadata.get('workflowRoot')
            if workflow_root_dir:
                rmtree(workflow_root_dir, ignore_errors=True)
        elif not workflow.failed:
            # TODO: after investigation remove all
            for input_directory in Path(workflow.metadata['workflowRoot']).glob('*/inputs'):
                print(f'Removing {input_directory}')
                rmtree(input_directory, True)

    @staticmethod
    def _synchronize_with_cromwell(workflow_id: str, workflow_step: str, attempts):
        try:
            workflow = Workflow.objects.get(id=workflow_id)
            if workflow.processed:
                return
            metadata = workflow.metadata
            workflow.status = metadata['status']
            workflow.save()
            attempts_left = attempts - 1
            if workflow.processing and attempts_left > 0:
                sleep(10)
                CromwellEvents._synchronize_with_cromwell(workflow_id, workflow_step, attempts_left)
            elif workflow.processed:
                CromwellEvents.workflow_ended(workflow)
        except Workflow.DoesNotExist as e:
            print(f'Workflow with id {workflow_id} does not exist')

    @staticmethod
    def on_workflow_update(workflow_id: str, workflow_step: str, potential_failure=True):
        retries = 1
        if potential_failure or workflow_step in ['call-nanoplot', 'call-quast']:
            retries = 12
        print(f'Updating workflow {workflow_id}, step {workflow_step}')
        Thread(target=CromwellEvents._synchronize_with_cromwell, args=(workflow_id, workflow_step, retries),
               daemon=True).start()
