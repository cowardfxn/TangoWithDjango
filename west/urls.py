from django.conf.urls import patterns, include, url
from west import views

urlpatterns = (
    url(r'^$', views.first_page),
)