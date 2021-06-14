from django.contrib import admin

from nanoforms_app.models import Dataset, Workflow

common = ('id', 'created_at', 'updated_at')


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = common + ('name', 'type', 'user', 'public', 'directory', 'number_of_files', 'size')
    list_editable = ('name', 'type', 'user', 'public', 'directory', 'number_of_files', 'size')


@admin.register(Workflow)
class WorkflowAdmin(admin.ModelAdmin):
    list_display = common + ('name', 'type', 'status', 'parent', 'user', 'public', 'dataset')
    list_editable = ('name', 'type', 'status', 'parent', 'user', 'public', 'dataset')
