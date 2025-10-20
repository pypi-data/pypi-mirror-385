from django.urls import path
from . import views

app_name = "django_sso_client_oauth"

urlpatterns = [
    path("login/", views.login, name="sso_login"),
    path("callback/", views.callback, name="sso_callback"),
]
