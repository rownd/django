import django


__version__ = "1.2.1"

if django.VERSION < (3, 2):
    default_app_config = "rownd_django.apps.RowndDjangoConfig"