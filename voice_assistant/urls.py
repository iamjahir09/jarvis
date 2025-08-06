from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='assistant-home'),
    path('process-voice/', views.process_voice, name='process-voice'),
]