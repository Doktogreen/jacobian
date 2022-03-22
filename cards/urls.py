from django.urls import path
from rest_framework import routers
from django.conf.urls import url, include
from . import views


urlpatterns = [
    path('debit', views.debit, name='debit'),
    path('reverse', views.reversal, name='debit'),
    path('enquiry', views.enquiry, name='enquiry'),
    path('health', views.health, name='health'),
    path('lien/debit', views.debit_lien, name='debit_lien'),
    path('lien/place', views.place_lien, name='place_lien'),
    path('', views.CardView.as_view(), name='card')
]
