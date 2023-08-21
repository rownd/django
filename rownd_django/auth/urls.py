from django.urls import path
from . import views

app_name = 'rownd_django'
urlpatterns = [
    path('session_authenticate', views.session_authenticate, name='session_authenticate'),
    path('session_sign_out', views.session_sign_out, name='session_sign_out'),
]