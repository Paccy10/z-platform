import os
from django.core.wsgi import get_wsgi_application

from .settings.base import env

os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"core.settings.{env('ENVIRONMENT')}")

application = get_wsgi_application()
