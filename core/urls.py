from django.urls import path
from core import views

urlpatterns = [
    path("", views.index, name="index"),
    path("select-roommate/", views.select_roommate, name="select_roommate"),
    path("switch-roommate/", views.switch_roommate, name="switch_roommate"),
    path("chores/new/", views.chore_create, name="chore_create"),
    path("chores/<int:chore_id>/edit/", views.chore_edit, name="chore_edit"),
    path("chores/<int:chore_id>/archive/", views.chore_archive, name="chore_archive"),
    path("chores/<int:chore_id>/done/", views.chore_mark_done, name="chore_mark_done"),
]
