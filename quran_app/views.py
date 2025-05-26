# quran_app/views.py
import httpx
import asyncio
from django.shortcuts import render
from django.http import Http404 # Keep for potential use later
from django.conf import settings
from django.utils.safestring import mark_safe
import json
from difflib import get_close_matches

async def fetch_equran_id_api(endpoint: str, params: dict = None):
    base_url = settings.EQURAN_API_BASE_URL
    if not base_url:
        print("!!! Error: EQURAN_API_BASE_URL is not configured in settings.py.")
        return {"error_message": "API base URL not configured."} # Return a dict with error
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"
            print(f"--- Fetching EQuran.id API: {url} with params: {params}")
            response = await client.get(url, params=params)
            
            print(f"--- API Response Status Code: {response.status_code} for {url}")
            
            response.raise_for_status()
            
            try:
                json_response = response.json()
                print(f"--- API JSON Response for {url} received successfully.")
                return json_response
            except json.JSONDecodeError as je:
                print(f"!!! JSONDecodeError for {url}: {je}. Response text: {response.text[:500]}")
                return {"error_message": "Failed to decode API JSON response.", "detail": response.text[:500]}

    except httpx.HTTPStatusError as e:
        error_detail = e.response.text[:500]
        print(f"!!! HTTPStatusError for {e.request.url}: {e.response.status_code} - {error_detail}")
        return {"error_message": f"API HTTP error: {e.response.status_code}", "detail": error_detail}
    except httpx.RequestError as e:
        print(f"!!! RequestError for {e.request.url}: {e}")
        return {"error_message": "API Request error", "detail": str(e)}
    except Exception as e:
        print(f"!!! Unexpected error in fetch_equran_id_api for {url}: {type(e).__name__} - {e}")
        return {"error_message": "Unexpected error during API fetch.", "detail": str(e)}

def format_qari_name_from_url(url_str: str) -> str:
    if not isinstance(url_str, str): return "Unknown Qari"
    try:
        name_part = url_str.split('/')[-2]
        return name_part.replace('-', ' ').replace('_', ' ').title()
    except IndexError: return "Unknown Qari"

def process_audio_options(audio_dict: dict):
    if not isinstance(audio_dict, dict): return {}
    formatted_options = {}
    for key, url in audio_dict.items():
        formatted_options[key] = {'url': url, 'name': format_qari_name_from_url(url)}
    return formatted_options

async def quran_home_view(request):
    surahs_list_from_api = [] # This will be populated by your fetch_equran_id_api call
    api_error = None
    suggestion = None
    query = request.GET.get('q_quran', '').strip()

    # Fetch all Surahs (ensure this part of your view works and populates surahs_list_from_api)
    try:
        response_wrapper = await fetch_equran_id_api("surat")
        if response_wrapper and response_wrapper.get('code') == 200 and 'data' in response_wrapper:
            raw_surahs = response_wrapper.get('data', [])
            if isinstance(raw_surahs, list):
                for surah_raw in raw_surahs:
                    surahs_list_from_api.append({ # Storing necessary fields
                        'nomor': surah_raw.get('nomor'),
                        'nama_latin': surah_raw.get('namaLatin'),
                        'arti': surah_raw.get('arti'),
                        # Add other fields you need for display if not searching on them
                        'nama_arabic': surah_raw.get('nama'),
                        'jumlah_ayat': surah_raw.get('jumlahAyat'),
                        'tempat_turun': surah_raw.get('tempatTurun'),
                        'deskripsi': mark_safe(surah_raw.get('deskripsi', '')),
                        'audio_full': surah_raw.get('audio')
                    })
            else:
                api_error = "Format data Surah dari API tidak sesuai."
        # ... (handle API errors as before) ...
        elif response_wrapper and response_wrapper.get('error_message'):
            api_error = f"API Error: {response_wrapper['error_message']} - {response_wrapper.get('detail', '')}"
        else:
            api_error = "Tidak dapat memuat daftar Surah atau respon tidak valid."
    except Exception as e:
        api_error = "Terjadi kesalahan saat memproses data Surah."
        print(f"Error in quran_home_view fetching surahs: {type(e).__name__} - {e}")


    displayed_surahs = []
    if query:
        query_lower = query.lower()
        displayed_surahs = [
            s for s in surahs_list_from_api if query_lower in s.get('nama_latin', '').lower() or \
                                            query_lower in s.get('arti', '').lower() or \
                                            query_lower == str(s.get('nomor'))
        ]

        # If no direct results, try to find a suggestion
        if not displayed_surahs and surahs_list_from_api:
            all_surah_names_latin = [s.get('nama_latin') for s in surahs_list_from_api if s.get('nama_latin')]
            close_matches = get_close_matches(query, all_surah_names_latin, n=1, cutoff=0.7) # Adjust cutoff as needed
            
            if close_matches:
                suggested_name = close_matches[0]
                for s_obj in surahs_list_from_api:
                    if s_obj.get('nama_latin') == suggested_name:
                        suggestion = {
                            'nomor': s_obj.get('nomor'),
                            'nama_latin': s_obj.get('nama_latin')
                        }
                        break
    else:
        displayed_surahs = surahs_list_from_api # Show all if no query

    return render(request, 'quran_app/quran_home.html', {
        'surahs': displayed_surahs,
        'query': query,
        'api_error': api_error,
        'suggestion': suggestion,
    })



async def surah_detail_view(request, surah_number):
    ayahs_with_tafsir = []
    surah_info = {}
    api_error = None 

    try:
        print(f"--- Starting surah_detail_view for Surah: {surah_number}")
        surah_response_wrapper = await fetch_equran_id_api(f"surat/{surah_number}")

        if not surah_response_wrapper or isinstance(surah_response_wrapper, dict) and surah_response_wrapper.get('error_message'):
            api_error = f"Failed to fetch Surah details: {surah_response_wrapper.get('error_message', 'Unknown API error')} - {surah_response_wrapper.get('detail', '') if isinstance(surah_response_wrapper, dict) else ''}"
            print(f"!!! {api_error}")
            return render(request, 'quran_app/surah_detail.html', {'api_error': api_error, 'surah_number_requested': surah_number, 'surah': {}, 'ayahs': []}) # FIXED PATH

        if not (isinstance(surah_response_wrapper, dict) and surah_response_wrapper.get('code') == 200 and 'data' in surah_response_wrapper):
            api_error = f"Invalid or unsuccessful API response for Surah details (Code: {surah_response_wrapper.get('code')})."
            print(f"!!! {api_error} - Response: {surah_response_wrapper}")
            return render(request, 'quran_app/surah_detail.html', {'api_error': api_error, 'surah_number_requested': surah_number, 'surah': {}, 'ayahs': []}) # FIXED PATH

        data_content = surah_response_wrapper['data']
        
        audio_full = data_content.get('audioFull', {})
        audio_full_options_formatted = process_audio_options(audio_full)
        default_qari_key = "05"
        default_surah_audio_url = audio_full.get(default_qari_key) 
        if not default_surah_audio_url and audio_full_options_formatted:
            first_qari_key = next(iter(audio_full_options_formatted))
            default_surah_audio_url = audio_full_options_formatted[first_qari_key]['url']

        surah_info = {
            'nomor': data_content.get('nomor', surah_number),
            'nama_latin': data_content.get('namaLatin'),
            'nama_arabic': data_content.get('nama'),
            'jumlah_ayat': data_content.get('jumlahAyat'),
            'tempat_turun': data_content.get('tempatTurun'),
            'arti': data_content.get('arti'),
            'deskripsi': mark_safe(data_content.get('deskripsi', '')),
            'audio_full_options_formatted': audio_full_options_formatted,
            'audio_default': default_surah_audio_url,
            'surat_selanjutnya': data_content.get('suratSelanjutnya'),
            'surat_sebelumnya': data_content.get('suratSebelumnya')
        }
        print(f"--- Surah Info Processed: {surah_info.get('nama_latin')}")

        raw_ayahs = data_content.get('ayat', [])
        temp_ayahs_map = {}
        if isinstance(raw_ayahs, list):
            for ayah_raw in raw_ayahs:
                ayah_nomor_in_surah = ayah_raw.get('nomorAyat')
                if ayah_nomor_in_surah is None: continue

                ayah_audio = ayah_raw.get('audio', {})
                ayah_audio_opts_formatted = process_audio_options(ayah_audio)
                default_ayah_audio = ayah_audio.get(default_qari_key)
                if not default_ayah_audio and ayah_audio_opts_formatted:
                    first_ayah_qari_key = next(iter(ayah_audio_opts_formatted))
                    default_ayah_audio = ayah_audio_opts_formatted[first_ayah_qari_key]['url']
                
                temp_ayahs_map[ayah_nomor_in_surah] = {
                    'nomor_ayat': ayah_nomor_in_surah,
                    'teks_arab': ayah_raw.get('teksArab'),
                    'teks_latin': ayah_raw.get('teksLatin'),
                    'teks_indonesia': ayah_raw.get('teksIndonesia'),
                    'audio_options_formatted': ayah_audio_opts_formatted,
                    'audio_ayah_default': default_ayah_audio,
                    'tafsir_text': ''
                }
            print(f"--- Processed {len(temp_ayahs_map)} ayahs into temp_ayahs_map.")
        else:
            api_error = "Ayah data ('ayat') from API is not a list or is missing."
            print(f"!!! {api_error}")

        if surah_info: 
            tafsir_response_wrapper = await fetch_equran_id_api(f"tafsir/{surah_number}")
            if not tafsir_response_wrapper or isinstance(tafsir_response_wrapper, dict) and tafsir_response_wrapper.get('error_message'):
                api_error_tafsir_msg = f"Failed to fetch Tafsir: {tafsir_response_wrapper.get('error_message', 'Unknown API error')} - {tafsir_response_wrapper.get('detail', '') if isinstance(tafsir_response_wrapper, dict) else ''}"
                print(f"!!! {api_error_tafsir_msg}")
                if api_error: api_error += f" | {api_error_tafsir_msg}" 
                else: api_error = api_error_tafsir_msg
            elif not (isinstance(tafsir_response_wrapper, dict) and tafsir_response_wrapper.get('code') == 200 and 'data' in tafsir_response_wrapper):
                api_error_tafsir_msg = f"Invalid or unsuccessful API response for Tafsir (Code: {tafsir_response_wrapper.get('code')})."
                print(f"!!! {api_error_tafsir_msg} - Response: {tafsir_response_wrapper}")
                if api_error: api_error += f" | {api_error_tafsir_msg}"
                else: api_error = api_error_tafsir_msg
            else:
                tafsir_data_content = tafsir_response_wrapper['data']
                if tafsir_data_content.get('nomor') != int(surah_number):
                    api_error_tafsir_msg = f"Tafsir data for wrong Surah: {tafsir_data_content.get('nomor')} vs {surah_number}."
                    print(f"!!! {api_error_tafsir_msg}")
                    if api_error: api_error += f" | {api_error_tafsir_msg}"
                    else: api_error = api_error_tafsir_msg
                else:
                    raw_tafsirs = tafsir_data_content.get('tafsir', [])
                    if isinstance(raw_tafsirs, list):
                        for tafsir_raw in raw_tafsirs:
                            ayah_num_for_tafsir = tafsir_raw.get('ayat')
                            if ayah_num_for_tafsir in temp_ayahs_map:
                                temp_ayahs_map[ayah_num_for_tafsir]['tafsir_text'] = mark_safe(tafsir_raw.get('teks', ''))
                        print(f"--- Merged tafsir for {len(raw_tafsirs)} ayahs.")
                    else:
                        api_error_tafsir_msg = "Tafsir items ('tafsir') is not a list or is missing."
                        print(f"!!! {api_error_tafsir_msg}")
                        if api_error: api_error += f" | {api_error_tafsir_msg}" 
                        else: api_error = api_error_tafsir_msg
            
            if temp_ayahs_map:
                ayahs_with_tafsir = list(temp_ayahs_map.values())
                if ayahs_with_tafsir:
                     ayahs_with_tafsir.sort(key=lambda x: x.get('nomor_ayat', 0))
        
        if not surah_info.get('nama_latin'): 
             if not api_error: api_error = f"Surah {surah_number} essential details could not be processed."
             print(f"!!! {api_error} - Surah Info was: {surah_info}")

    except Exception as e:
        error_type = type(e).__name__
        print(f"!!! CRITICAL Error in surah_detail_view for surah {surah_number}: {error_type} - {e}")
        api_error = f"An unexpected critical error occurred: {error_type} - {str(e)}"
        surah_info = {} 
        ayahs_with_tafsir = []

    if not surah_info.get('nomor') and not ayahs_with_tafsir and not api_error:
        api_error = f"Data for Surah {surah_number} is unavailable or could not be loaded."

    print(f"--- Rendering surah_detail.html for Surah {surah_number} with error: {api_error}")
    return render(request, 'quran_app/surah_detail.html', { # FIXED PATH
        'surah': surah_info,
        'ayahs': ayahs_with_tafsir,
        'api_error': api_error,
        'surah_number_requested': surah_number
    })