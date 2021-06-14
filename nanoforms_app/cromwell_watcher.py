import logging
import os
from threading import Thread

from watchgod import watch, Change, DefaultWatcher

from nanoforms.settings import CROMWELL_EXECUTION_DIR

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(name)s %(levelname)s %(message)s',
)


class CustomWatcher(DefaultWatcher):

    def _watch_file(self, path, changes, new_files):
        try:
            super()._watch_file(path, changes, new_files)
        except:
            pass

    def _walk_dir(self, dir_path, changes, new_files):
        try:
            super()._walk_dir(dir_path, changes, new_files)
        except:
            pass


class CromwellWatcher:

    @staticmethod
    def _run(workload_name):
        d = CROMWELL_EXECUTION_DIR + workload_name
        logging.info(f'Watcher started in dir: {d}')
        for changes in watch(d, watcher_cls=CustomWatcher):
            for change in changes:
                if change[0] == Change.added:
                    path = str(change[1])
                    try:
                        path_split = path.split('/')
                        if path_split[-2] == 'execution':
                            file_name = path_split[-1]
                            workflow_step = path_split[-3]
                            workflow_id = path_split[-4]
                            if file_name in ['script', 'rc']:
                                rc = 0
                                try:
                                    if file_name == 'rc':
                                        rc = int(open(path).read().strip())
                                except:
                                    rc = 1
                                from nanoforms_app.cromwell_events import CromwellEvents
                                CromwellEvents.on_workflow_update(workflow_id, workflow_step, rc != 0)
                    except:
                        logging.error(f'Watcher can not process {path}')

    @staticmethod
    def run(workload_name):
        if not os.environ.get("WATCHER_INITIALIZED" + workload_name):
            try:
                Thread(target=CromwellWatcher._run, args=(workload_name,), daemon=True).start()
                os.environ["WATCHER_INITIALIZED" + workload_name] = "True"
            except:
                logging.error('Watcher failed ' + workload_name)
