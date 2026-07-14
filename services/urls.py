from django.urls import path

from . import views

urlpatterns = [
    path(
        "categories/",
        views.get_categories,
        name="get-categories",
    ),
]
