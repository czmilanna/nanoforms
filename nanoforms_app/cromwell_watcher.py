import logging
import os
from threading import Thread
from time import sleep

logger = logging.getLogger(__name__)


class CromwellWatcher:

    @staticmethod
    def _run():
        while True:
            try:
                from nanoforms_app.models import Workflow
                from nanoforms_app.cromwell import workflow_metadata

                running_workflows = Workflow.objects.filter(status__in=['Submitted', 'Running'])
                for workflow in running_workflows:
                    metadata = workflow_metadata(workflow.id)
                    cromwell_status = metadata['status']
                    if workflow.status != cromwell_status:
                        workflow.status = cromwell_status
                        workflow.save()
                        if workflow.processed:
                            from nanoforms_app.cromwell_events import CromwellEvents
                            CromwellEvents.workflow_ended(workflow)
            except:
                logging.warning('Cromwell Watcher warning on single run')
            sleep(60)

    @staticmethod
    def run():
        if not os.environ.get("WATCHER_INITIALIZED"):
            try:
                Thread(target=CromwellWatcher._run, args=(), daemon=True).start()
                os.environ["WATCHER_INITIALIZED"] = "True"
            except:
                logging.error('Cromwell Watcher failed ')
