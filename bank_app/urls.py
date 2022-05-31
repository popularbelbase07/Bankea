from django.contrib import admin
from django.urls import path, include
from . import views

app_name = 'bank_app'

urlpatterns = [
    path('', views.home, name='home'),
    path('bank_app/staff_page/', views.staff_page, name='staff_page')
]
