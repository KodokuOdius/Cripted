from django.contrib import admin
from django.urls import path, include
from . import views


urlpatterns = [
    # path("", views.index, name="index")
    path("", views.HomeView.as_view(), name="main"),
    path("create/", views.CreateUser.as_view(), name="create"),
    path("api/passform", views.passform),
    path("api/modalpass", views.modalpass)
]