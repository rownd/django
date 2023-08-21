from django.apps import AppConfig

from .auth import client

class RowndDjangoConfig(AppConfig):
    name = 'rownd_django'
    verbose_name = 'Rownd'
    def ready(self):
        # Fetch the Rownd app's app config at startup
        client.RowndAppConfig().config