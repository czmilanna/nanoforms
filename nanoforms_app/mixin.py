from django.http import HttpResponseForbidden
from django.views.generic.detail import BaseDetailView


class OwnerAccessMixin(BaseDetailView):

    def dispatch(self, request, *args, **kwargs):
        o = self.get_object()

        if o.user == self.request.user:
            return super(OwnerAccessMixin, self).dispatch(request, *args, **kwargs)

        return HttpResponseForbidden()


class OwnerOrAdminOrPublicAccessMixin(BaseDetailView):

    def dispatch(self, request, *args, **kwargs):
        o = self.get_object()

        if o.user == self.request.user or request.user.is_superuser or o.public:
            return super(OwnerOrAdminOrPublicAccessMixin, self).dispatch(request, *args, **kwargs)

        return HttpResponseForbidden()
