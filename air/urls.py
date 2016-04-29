"""lingualsearch URL Configuration
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^check_login','air.views.check_login'),
    url(r'^$', 'air.views.login'),
    url(r'dashboard', views.display_dashboard, name='display_dashboard'),
    url(r'check_players', views.suggestor, name='suggestor'),
    url(r'replace_players', views.replace_players, name='replace_players'),
    url(r'redirectToDash', views.deletePlayer, name='deletePlayer'),
    url(r'redirectToAddPlayer', views.addPlayerTeam, name='addPlayerTeam'),
    url(r'add_player', views.suggestor_addPlayer, name='suggestor_addPlayer'),
]
