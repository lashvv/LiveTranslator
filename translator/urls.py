from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload-audio/', views.upload_audio, name='upload-audio'),
]