# hadith_app/views.py
from django.shortcuts import render
import httpx
import os
import json
import pprint # For debugging
from dotenv import load_dotenv
from pathlib import Path # For robust .env path finding

# --- Environment Variable Loading ---
# Determine the Project's Base Directory more robustly
# This assumes views.py is in hadith_app/, and hadith_app/ is in the project root
# where manage.py and .env reside.
try:
    BASE_DIR = Path(__file__).resolve().parent.parent
    dotenv_path = BASE_DIR / '.env'
    # print(f"[Debug Views] Attempting to load .env from: {dotenv_path}")
    if dotenv_path.exists():
        load_dotenv(dotenv_path=dotenv_path)
        # print(f"[Debug Views] .env loaded from {dotenv_path}. API_BASE_URL from env: {os.getenv('HADITH_API_BASE_URL')}")
    else:
        print(f"Warning: .env file not found at {dotenv_path}. Trying default load_dotenv().")
        # Fallback to default load_dotenv() which searches CWD and parents
        if load_dotenv():
             print(f"[Debug Views] .env loaded via default search. API_BASE_URL from env: {os.getenv('HADITH_API_BASE_URL')}")
        else:
            print(f"[Debug Views] Default load_dotenv() also failed to find .env.")

except Exception as e:
    print(f"Error determining .env path or loading .env: {e}")

API_BASE_URL = os.getenv('HADITH_API_BASE_URL')
if not API_BASE_URL:
    print("Warning: HADITH_API_BASE_URL not resolved from .env. Using hardcoded default.")
    API_BASE_URL = "https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1"
# else:
#    print(f"[Debug Views] API_BASE_URL is set to: {API_BASE_URL}")

EDITIONS_API_URL = f"{API_BASE_URL}/editions.json"
# --- End Environment Variable Loading ---


def fetch_api_data(url: str, is_json: bool = True):
    """Helper function to fetch data from a URL using httpx."""
    try:
        # print(f"[Debug fetch_api_data] Requesting URL: {url}")
        with httpx.Client(timeout=10.0) as client:
            response = client.get(url)
            response.raise_for_status()
            if is_json:
                return response.json()
            return response.text
    except httpx.HTTPStatusError as e:
        print(f"HTTP error fetching API data from {url}: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        print(f"Request error fetching API data from {url}: {e}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {url}: {e}")
    return None

# Page 1: List of all Hadith Collections
def hadith_home_view(request):
    all_editions_data = fetch_api_data(EDITIONS_API_URL)
    collections_display = {}
    if all_editions_data and isinstance(all_editions_data, dict):
        for collection_key, data in all_editions_data.items():
            if isinstance(data, dict):
                collections_display[collection_key] = {
                    'name': data.get('name', collection_key.title()),
                    'key': collection_key
                }
    context = {'hadith_collections': collections_display}
    return render(request, 'hadith_app/hadith_home.html', context)

# Page 2: List of Editions (languages) for a selected Collection
def hadith_collection_editions_view(request, collection_key):
    all_editions_data = fetch_api_data(EDITIONS_API_URL)
    collection_info = None
    if all_editions_data and isinstance(all_editions_data, dict) and collection_key in all_editions_data:
        data = all_editions_data[collection_key]
        if isinstance(data, dict):
            editions = data.get('collection', [])
            if editions is None: editions = []
            if all(isinstance(e, dict) for e in editions):
                 editions.sort(key=lambda x: x.get('language', ''))
            collection_info = {
                'name': data.get('name', collection_key.title()),
                'key': collection_key,
                'editions': editions
            }
    context = {'collection_info': collection_info, 'collection_key': collection_key}
    return render(request, 'hadith_app/hadith_collection_editions.html', context)


# Page 3: List of Sections for a selected Collection & Edition
def hadith_edition_sections_view(request, collection_key, edition_name):
    all_editions_data = fetch_api_data(EDITIONS_API_URL)
    edition_main_json_url = None
    collection_proper_name = collection_key.title()
    edition_language = "Unknown"
    sections_list_data = None
    section_details_data = None # Initialize to None


    if all_editions_data and isinstance(all_editions_data, dict) and collection_key in all_editions_data:
        collection_main_data = all_editions_data.get(collection_key)
        if isinstance(collection_main_data, dict):
            collection_proper_name = collection_main_data.get('name', collection_proper_name)
            editions_in_collection = collection_main_data.get('collection', [])
            if editions_in_collection is None: editions_in_collection = []

            for edition_info in editions_in_collection:
                if isinstance(edition_info, dict) and edition_info.get('name') == edition_name:
                    edition_main_json_url = edition_info.get('linkmin') or edition_info.get('link')
                    edition_language = edition_info.get('language', "Unknown")
                    break 
    

    if edition_main_json_url:
        full_edition_data = fetch_api_data(edition_main_json_url)
        
         
        if full_edition_data and isinstance(full_edition_data, dict):
            metadata = full_edition_data.get('metadata') 
            
            if isinstance(metadata, dict):
                collection_proper_name = metadata.get('name', collection_proper_name)
                
                sections_from_api = metadata.get('sections')
                if isinstance(sections_from_api, dict):
                    temp_sections_list = []
                    for num_str, title in sections_from_api.items():
                        if not title and num_str == "0": 
                            continue
                        try:
                            num_int_for_sorting = int(num_str)
                            temp_sections_list.append({'number': num_str, 'title': title, 'numeric_key': num_int_for_sorting})
                        except ValueError:
                            temp_sections_list.append({'number': num_str, 'title': title, 'numeric_key': float('inf')}) 
                    temp_sections_list.sort(key=lambda x: x['numeric_key'])
                    sections_list_data = temp_sections_list
                
                section_detail_from_api = metadata.get('section_details')
                
                if isinstance(section_detail_from_api, dict):
                    section_details_data = section_detail_from_api 
                    

    context = {
        'collection_key': collection_key,
        'edition_name': edition_name,
        'collection_name': collection_proper_name,
        'edition_language': edition_language,
        'sections': sections_list_data,
        'section_details': section_details_data, 
        'error_message': "Could not load sections for this edition." if not sections_list_data and edition_main_json_url else None
    }
    
    
    return render(request, 'hadith_app/hadith_edition_sections.html', context)

# Page 4: List of Hadiths for a specific Section
def hadith_section_detail_view(request, collection_key, edition_name, section_no):
    section_api_url = f"{API_BASE_URL}/editions/{edition_name}/sections/{section_no}.json"
    section_content = fetch_api_data(section_api_url)
    
    collection_proper_name = collection_key.title()
    edition_language = "Unknown"
    section_title_from_metadata = f"Section {section_no}"

    all_editions_data = fetch_api_data(EDITIONS_API_URL)
    if all_editions_data and isinstance(all_editions_data, dict) and collection_key in all_editions_data:
        collection_main_data = all_editions_data[collection_key]
        if isinstance(collection_main_data, dict):
            collection_proper_name = collection_main_data.get('name', collection_proper_name)
            editions = collection_main_data.get('collection', [])
            if editions is None: editions = []
            for ed in editions:
                if isinstance(ed, dict) and ed.get('name') == edition_name:
                    edition_language = ed.get('language', edition_language)
                    break

    current_metadata = None
    hadiths_list = []
    if section_content and isinstance(section_content, dict):
        current_metadata = section_content.get('metadata')
        hadiths_list = section_content.get('hadiths', [])
        if isinstance(current_metadata, dict):
            collection_proper_name = current_metadata.get('name', collection_proper_name)
            current_section_info = current_metadata.get('section')
            if isinstance(current_section_info, dict) and section_no in current_section_info:
                section_title_from_metadata = current_section_info[section_no]
    
    context = {
        'collection_key': collection_key,
        'edition_name': edition_name,
        'section_no': section_no,
        'collection_name': collection_proper_name,
        'edition_language': edition_language,
        'section_title': section_title_from_metadata,
        'metadata': current_metadata, # This will contain section_detail for the current section
        'hadiths': hadiths_list,
        'error_message': "Hadith data for this section could not be loaded." if not section_content else None
    }
    return render(request, 'hadith_app/hadith_list.html', context)