from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^index/$', views.index, name='index'),
    url(r'^index.html/$', views.index, name='index'),
    url(r'^alerts/$', views.alerts, name='alerts'),
    url(r'^test/$', views.test, name='test'),
    url(r'^subscribe/$', views.subscribe, name='subscribe'),
    url(r'^unsub/$', views.unsub, name='unsub'),
    url(r'^readnotification/$', views.readnotification, name='readnotification'),
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^create-account/$', views.create_account, name='create_account'),

    #get
    url(r'^get-stations/$', views.get_stations, name='get_stations'),
]

