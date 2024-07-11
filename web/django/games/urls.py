from django.urls import include, path
from django.utils.translation import gettext_lazy as _
from . import views

urlpatterns = [
    path('tournaments/', ...), # GET, POST
    path('tournaments/<uuid:tournament_id>/', ...), # GET
    path('tournaments/<uuid:tournament_id>/join/', ...), # POST
    path('tournaments/<uuid:tournament_id>/leave/', ...), # POST
    path('tournaments/<uuid:tournament_id>/ready/', ...), # POST
    path('tournaments/<uuid:tournament_id>/start/', ...), # POST
    path('tournaments/search/', ...), # GET
]