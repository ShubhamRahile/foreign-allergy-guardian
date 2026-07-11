import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foreign_allergy_guardian.settings')
application = get_wsgi_application()
