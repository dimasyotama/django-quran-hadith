# hadith_app/urls.py
from django.urls import path
from . import views

app_name = 'hadith_app'

urlpatterns = [
    # Page 1: List of all Hadith Collections
    path('', views.hadith_home_view, name='hadith_home'),
    
    # Page 2: List of Editions (languages) for a selected Collection
    path('<str:collection_key>/', views.hadith_collection_editions_view, name='hadith_collection_editions'),
    
    # Page 3: List of Sections (books/chapters) for a selected Collection & Edition
    path('<str:collection_key>/<str:edition_name>/', views.hadith_edition_sections_view, name='hadith_edition_sections'),
    
    # Page 4: List of Hadiths for a specific Section
    path('<str:collection_key>/<str:edition_name>/section/<str:section_no>/', views.hadith_section_detail_view, name='hadith_section_detail'),
]