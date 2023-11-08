from django.urls import re_path
from web import views_home
from .views import AttemptsView


urlpatterns = [
    re_path(r'^$', views_home.home),
    re_path(r'/attempts/', AttemptsView.as_view())
]
