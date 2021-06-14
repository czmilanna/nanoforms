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
import os

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include
from django.views.generic import RedirectView
from django_registration.backends.one_step.views import RegistrationView

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('health/', lambda r: HttpResponse('healthy')),
                  path('accounts/profile/', RedirectView.as_view(url='/', permanent=False)),
                  path('accounts/', include('django.contrib.auth.urls')),
                  path('', include("nanoforms_app.urls"))
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if os.environ.get('EMAIL_HOST'):
    urlpatterns += [
        path('accounts/', include('django_registration.backends.activation.urls'))
    ]
else:
    urlpatterns += [
        path('accounts/register/', RegistrationView.as_view(success_url='/'), name='django_registration_register'),
        path('accounts/', include('django_registration.backends.one_step.urls'))
    ]
