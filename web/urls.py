from django.urls import re_path
from web import views_home

urlpatterns = [
    re_path(r'^$', views_home.home),
]
