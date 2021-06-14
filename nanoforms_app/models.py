import os
import shutil
import uuid
from shutil import rmtree

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from threadlocals.threadlocals import get_current_request

from nanoforms.settings import BASE_UPLOAD_DIR, CROMWELL_EXECUTION_DIR
from nanoforms_app.convert import sizeof_fmt
from nanoforms_app.cromwell import workflow_metadata, workflow_outputs, workflow_abort


class Base(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Dataset(Base):
    class DatasetType(models.TextChoices):
        NANOPORE = 'N', _('Nanopore sequencing data')
        ILLUMINA = 'I', _('Ilumina sequencing data')

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    directory = models.CharField(max_length=500)
    name = models.CharField(max_length=100)
    number_of_files = models.IntegerField()
    size = models.CharField(max_length=100)
    public = models.BooleanField(default=False)
    type = models.CharField(
        max_length=10,
        choices=DatasetType.choices,
        default=DatasetType.NANOPORE
    )

    def quality_workflows(self):
        request = get_current_request()
        access = Q(user=request.user) | Q(public=True)
        return self.workflow_set.filter(access & Q(type=Workflow.WorkflowType.QUALITY)).order_by('created_at')

    def assembly_workflows(self):
        request = get_current_request()
        access = Q(user=request.user) | Q(public=True)
        return self.workflow_set.filter(access & Q(type=Workflow.WorkflowType.ASSEMBLY)).order_by('created_at')

    def files(self):
        result = []
        for root, dirs, files in os.walk(self.directory):
            for name in files:
                filename = os.path.join(root, name)
                stats = os.stat(filename)
                result.append({
                    'name': name,
                    'size': sizeof_fmt(stats.st_size)
                })
        return result

    def __str__(self):
        return self.name


@receiver(post_delete, sender=Dataset)
def my_handler(sender, **kwargs):
    try:
        directory = str(kwargs.get('instance').directory)
        if directory.startswith(BASE_UPLOAD_DIR) and len(BASE_UPLOAD_DIR) < len(directory):
            shutil.rmtree(directory, ignore_errors=True)
    except:
        print('Handler post delete for dataset failed')


class Workflow(Base):
    class WorkflowType(models.TextChoices):
        QUALITY = 'Q', _('Quality')
        ASSEMBLY = 'A', _('Assembly')
        HYBRID = 'H', _('Hybrid')
        OTHER = '-', _('Other')

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    secondary_dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='secondary_dataset',
                                          null=True)
    name = models.CharField(max_length=100)
    type = models.CharField(
        max_length=10,
        choices=WorkflowType.choices,
        default=WorkflowType.OTHER
    )
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(
        max_length=20,
        default='Submitted'
    )
    public = models.BooleanField(default=False)

    def __init__(self, *args, **kwargs):
        self._metadata = None
        self._output = None
        self._quality = None
        super().__init__(*args, **kwargs)

    def __str__(self):
        return self.name

    def assemblies(self):
        request = get_current_request()
        access = Q(user=request.user) | Q(public=True)
        return self.workflow_set.filter(access & Q(type=Workflow.WorkflowType.ASSEMBLY)).order_by('created_at')

    @property
    def quality(self):
        if self.parent:
            return self.parent
        elif not self._quality:
            self._quality = Workflow.objects.filter(type=Workflow.WorkflowType.QUALITY, dataset=self.dataset).first()
        return self._quality

    @property
    def metadata(self):
        if not self._metadata:
            print('get metadata')
            self._metadata = workflow_metadata(self.id)
        return self._metadata

    @property
    def failure(self):
        try:
            calls = self.metadata['calls']
            err = next(c for ck, [c] in calls.items() if c['executionStatus'] == 'Failed')
            try:
                msg = open(err['stderr']).read().replace('\n', '<br/>')
            except:
                msg = open(err['stderr'] + '.background').read().replace('\n', '<br/>')
            msg = msg.replace(CROMWELL_EXECUTION_DIR, '')
            msg = msg.replace('/cromwell-executions/prz_prepare_data', '')
            msg = msg.replace('/cromwell-executions/prz_data_assembly', '')
            msg = msg.replace('/cromwell-executions/prz_hybrid_assembly', '')
        except:
            msg = 'No error file generated'
        msg += '<br/>Try running with different parameters.'
        return mark_safe(msg)

    @property
    def output(self):
        if not self._output:
            print('get output')
            self._output = workflow_outputs(self.id)
        return self._output

    @property
    def submitted(self):
        return self.status == 'Submitted'

    @property
    def running(self):
        return self.status == 'Running'

    @property
    def succeeded(self):
        return self.status == 'Succeeded'

    @property
    def aborted(self):
        return self.status == 'Aborted'

    @property
    def failed(self):
        return self.status == 'Failed'

    @property
    def processing(self):
        return self.status in [
            'On Hold',
            'Submitted',
            'Running',
            'Aborting'
        ]

    @property
    def processed(self):
        return self.status in [
            'Aborted',
            'Succeeded',
            'Failed'
        ]

    @property
    def refresh_after_ms(self):
        seconds_from_start = (timezone.now() - self.created_at).seconds
        if seconds_from_start < 30:
            return 3000
        elif seconds_from_start < 120:
            return 10000
        else:
            return 30000


@receiver(post_delete, sender=Workflow)
def my_handler(sender, **kwargs):
    try:
        workflow: Workflow = kwargs.get('instance')
        if workflow.processing:
            workflow.status = 'Aborting'
            workflow_abort(workflow.id)
        else:
            workflow_root_dir = workflow.metadata.get('workflowRoot')
            if workflow_root_dir:
                rmtree(workflow_root_dir, ignore_errors=True)
    except:
        print('Handler post delete for workflow failed')
