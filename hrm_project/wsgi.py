"""
WSGI config for hrm_project project.
"""

import os

import sys

# Add apps/ to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'apps'))

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrm_project.settings.production')

application = get_wsgi_application()
