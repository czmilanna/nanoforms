"""nanoforms URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import path

from nanoforms_app import views
from nanoforms_app.access import required_login_or_public

urlpatterns = [
    path('', lambda request: redirect('home/', permanent=True)),
    path('home/', views.index, name='index'),
    path('help/', views.help, name='help'),
    path('about/', views.about, name='about'),

    path('dataset/', required_login_or_public(views.DatasetListView.as_view()), name='dataset'),
    path('dataset/create', login_required(views.DatasetCreateView.as_view()), name='dataset_create'),
    path('dataset/<uuid:pk>/', required_login_or_public(views.DatasetDetailView.as_view()), name='dataset_details'),
    path('dataset/<uuid:dataset_id>/file_options/<int:select_idx>', required_login_or_public(views.file_options), name='dataset_file_options'),
    path('dataset/<uuid:pk>/delete', login_required(views.DeleteDatasetView.as_view()), name='dataset_delete'),

    path('workflow/<uuid:pk>/delete', login_required(views.WorkflowDeleteView.as_view()), name='workflow_delete'),
    path('quality/', required_login_or_public(views.QualityListView.as_view()), name='quality'),
    path('quality/create', login_required(views.QualityCreateView.as_view()), name='quality_create'),
    path('quality/<uuid:pk>/', required_login_or_public(views.QualityDetailView.as_view()), name='quality_detail'),
    path('quality-<uuid:workflow_id>.zip', required_login_or_public(views.download_quality_report), name='quality_report'),

    path('assembly/', required_login_or_public(views.AssemblyListView.as_view()), name='assembly'),
    path('assembly/create', login_required(views.AssemblyCreateView.as_view()), name='assembly_create'),
    path('assembly/<uuid:pk>/', required_login_or_public(views.AssemblyDetailView.as_view()), name='assembly_detail'),
    path('report-<uuid:workflow_id>.zip', required_login_or_public(views.download_assembly_report), name='assembly_report'),

    path('hybrid/create', login_required(views.HybridAssemblyCreateView.as_view()), name='hybrid_create'),
    path('hybrid/<uuid:pk>/', required_login_or_public(views.HybridAssemblyDetailView.as_view()), name='hybrid_detail'),
    path('hybrid_report-<uuid:workflow_id>.zip', required_login_or_public(views.download_hybrid_report), name='hybrid_report'),

    path('metadata/<uuid:workflow_id>/', required_login_or_public(views.metadata), name='metadata'),
    path('assembly_details/<uuid:workflow_id>/', required_login_or_public(views.assembly_details), name='assembly_details'),
    path('hybrid_metadata/<uuid:workflow_id>/', required_login_or_public(views.hybrid_metadata), name='hybrid_metadata'),
    path('hybrid_details/<uuid:workflow_id>/', required_login_or_public(views.hybrid_details), name='hybrid_details'),

    path('status/<uuid:workflow_id>', required_login_or_public(views.status), name='status'),
    path('step/<uuid:workflow_id>', required_login_or_public(views.step), name='step'),
    path('timing/<uuid:workflow_id>', required_login_or_public(views.timing), name='timing'),
    path('nanoplot/<uuid:workflow_id>', required_login_or_public(views.nanoplot), name='nanoplot'),
    path('quast/<uuid:workflow_id>', required_login_or_public(views.quast), name='quast'),
    path('hybrid_quast/<uuid:workflow_id>', required_login_or_public(views.hybrid_quast), name='hybrid_quast'),
    path('krona_report/<uuid:workflow_id>', required_login_or_public(views.krona_report), name='krona_report'),
    path('krona_report_txt/<uuid:workflow_id>', required_login_or_public(views.krona_report_txt), name='krona_report'),
    path('download/<uuid:workflow_id>/<str:output_key>/<str:file_name>', required_login_or_public(views.download),
         name='download')
]
