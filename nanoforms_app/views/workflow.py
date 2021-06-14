from django.urls import reverse
from django.views import generic

from nanoforms_app.mixin import OwnerAccessMixin
from nanoforms_app.models import Workflow


class WorkflowDeleteView(OwnerAccessMixin, generic.DeleteView):
    model = Workflow

    def get_success_url(self):
        return self.request.GET.get('next', reverse('index'))
