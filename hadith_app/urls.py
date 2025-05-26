# hadith_app/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.hadith_home_view, name='hadith_home'),
    path('book/<slug:book_slug>/', views.hadith_list_view, name='hadith_list'),
]