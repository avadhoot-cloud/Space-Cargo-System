"""
WSGI config for spacecargo project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spacecargo.settings')

# Use a simple WSGI application wrapper for faster startup
class WSGIApplicationWithHealthCheck:
    def __init__(self, app):
        self.app = app
        
    def __call__(self, environ, start_response):
        # Quick health check route - responds immediately without Django overhead
        if environ['PATH_INFO'] == '/':
            status = '200 OK'
            headers = [('Content-type', 'application/json')]
            start_response(status, headers)
            return [b'{"status":"online"}']
        return self.app(environ, start_response)

# Get the Django WSGI application
django_app = get_wsgi_application()

# Wrap it with our health check
application = WSGIApplicationWithHealthCheck(django_app)
