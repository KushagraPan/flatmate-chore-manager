from django.urls import path
from core import views

urlpatterns = [
    path("", views.index, name="index"),
    path("select-roommate/", views.select_roommate, name="select_roommate"),
    path("switch-roommate/", views.switch_roommate, name="switch_roommate"),
]
