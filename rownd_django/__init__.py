import django


__version__ = "1.0.0"

if django.VERSION < (3, 2):
    default_app_config = "rownd_django.apps.RowndDjango"