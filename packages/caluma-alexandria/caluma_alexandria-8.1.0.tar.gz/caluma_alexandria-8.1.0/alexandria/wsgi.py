"""
WSGI config for project_app2 project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os

from django.conf import settings
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alexandria.settings.django")

if settings.ALEXANDRIA_USE_MANABI:
    from alexandria.dav import get_dav

    wsgi_dav = get_dav()
    wsgi_django = get_wsgi_application()

    def dispatch(environ, start_response):
        path = environ["PATH_INFO"] or "/"
        dav_prefix = settings.ALEXANDRIA_MANABI_DAV_URL_PATH
        if path.startswith(dav_prefix):
            environ = environ.copy()
            environ["SCRIPT_NAME"] = environ.get("SCRIPT_NAME", "") + dav_prefix
            return wsgi_dav(environ, start_response)
        else:
            return wsgi_django(environ, start_response)

    application = dispatch
else:
    application = get_wsgi_application()
