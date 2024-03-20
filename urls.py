from django.urls import path

from aadoctrinecontracts import views

app_name = "aadoctrinecontracts"

urlpatterns = [
    path("", views.index, name="index"),
]
