from django.conf.urls import url
from web import views_home

urlpatterns = [
    url(r'^$', views_home.home),
]
