# quran_app/urls.py
from django.urls import path
from . import views

app_name = 'quran_app'

urlpatterns = [
    path('', views.quran_home_view, name='quran_home'),
    path('surah/<int:surah_number>/', views.surah_detail_view, name='surah_detail'),
]