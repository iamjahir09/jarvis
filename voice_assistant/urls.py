from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('process-voice/', views.process_voice, name='process_voice'),
]