"""
WSGI config for nanoforms project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

from nanoforms_app.cromwell_watcher import CromwellWatcher

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nanoforms.settings')

application = get_wsgi_application()

CromwellWatcher.run()
