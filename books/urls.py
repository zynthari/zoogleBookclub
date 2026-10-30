from django.urls import path

from . import views

urlpatterns = [
    path("", views.welcome, name="welcome"),
    path("csrf", views.csrf_token, name="csrf_token"),
    path("get_question", views.get_question, name="get_question"),
    path("upload_library", views.upload_library, name="upload_library"),
]
