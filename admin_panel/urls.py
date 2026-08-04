from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.admin_login),
    path("create/", views.create_admin),
]