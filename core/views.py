import json
import httpx 
import asyncio
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings

async def fetch_prayer_times_api(city, country, method):
    """
    Asynchronous helper function to fetch prayer times from Aladhan API,
    explicitly handling redirects.
    """
    base_url = settings.PRAYER_TIMES_API_BASE_URL # Should be 'https://api.aladhan.com/v1'
    if not all([base_url, city, country, method]):
        print("Error: Prayer times API settings are not fully configured.")
        return {"error": "Prayer API settings incomplete."}

    endpoint = "timingsByCity"
    params = {
        "city": city,
        "country": country,
        "method": method
    }
    
    url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"
    print(f"Attempting to fetch Prayer Times API data from: {url} with params: {params}")

    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=20.0) as client: # Explicitly allow redirects
            response = await client.get(url, params=params)
            
            # Log history if redirects occurred
            if response.history:
                print("Request was redirected:")
                for r in response.history:
                    print(f"  {r.status_code} -> {r.headers['location']}")
                print(f"Final URL: {response.url} with status: {response.status_code}")

            # Check the status code of the FINAL response after all redirects
            if response.status_code == 200:
                return response.json()
            else:
                # If it's not 200 after following redirects, then it's an issue.
                print(f"HTTP error after potential redirects. Final status: {response.status_code} from {response.url} - {response.text}")
                return {"error": f"API returned status {response.status_code}", "detail": response.text[:200]} # Truncate detail

    except httpx.HTTPStatusError as e: # This might not be hit if we check status_code manually
        print(f"HTTPStatusError (should be caught by status_code check): {e.request.url} - {e.response.status_code}")
        return {"error": f"HTTP error: {e.response.status_code}", "detail": e.response.text[:200]}
    except httpx.RequestError as e:
        print(f"RequestError fetching Prayer Times ({e.request.url}): {e}")
        return {"error": "Request error", "detail": str(e)}
    except Exception as e:
        print(f"Unexpected error in fetch_prayer_times_api for {url}: {type(e).__name__} - {e}")
        return {"error": "Unexpected API fetch error", "detail": str(e)} 

async def translate_text_with_gemini_api(text_to_translate, target_language="id", source_language="en"):
    """
    Asynchronous conceptual placeholder for Gemini translation.
    In a real scenario, you'd use the official Google AI client library.
    If it were a direct HTTP API, you'd use httpx here.
    """

    # Simulating an async operation for the mock
    await asyncio.sleep(0.1) # Simulate network delay

    if target_language == "id":
        return f"{text_to_translate} (diterjemahkan ke Bahasa Indonesia - MOCK ASYNC)"
    return f"{text_to_translate} (translated to {target_language} - MOCK ASYNC)"

async def home_view(request):
    context = {}
    prayer_times_data = await fetch_prayer_times_api(
        settings.PRAYER_TIMES_CITY,
        settings.PRAYER_TIMES_COUNTRY,
        settings.PRAYER_TIMES_METHOD
    )

    if prayer_times_data and prayer_times_data.get('code') == 200 and 'data' in prayer_times_data:
        timings = prayer_times_data['data'].get('timings', {})
        relevant_times = {
            "Imsak": timings.get("Imsak"),
            "Subuh": timings.get("Fajr"),
            "Terbit": timings.get("Sunrise"),
            "Dzuhur": timings.get("Dhuhr"),
            "Ashar": timings.get("Asr"),
            "Maghrib": timings.get("Maghrib"),
            "Isya": timings.get("Isha")
        }
        context['prayer_times'] = relevant_times
        context['prayer_times_json'] = json.dumps(relevant_times) # For JS countdown
        
        date_info = prayer_times_data['data'].get('date', {})
        context['prayer_date_readable'] = date_info.get('readable')
        
        hijri_info = date_info.get('hijri', {})
        if hijri_info:
            context['hijri_date_details'] = {
                'day': hijri_info.get('day'),
                'month_ar': hijri_info.get('month', {}).get('ar'),
                'month_en': hijri_info.get('month', {}).get('en'),
                'year': hijri_info.get('year'),
                'designation': hijri_info.get('designation', {}).get('abbreviated'),
                'holidays': hijri_info.get('holidays', [])
            }
            context['prayer_hijri_date_readable'] = f"{hijri_info.get('day')} {hijri_info.get('month', {}).get('en')} {hijri_info.get('year')} {hijri_info.get('designation', {}).get('abbreviated')}"
        else:
            context['hijri_date_details'] = None
            context['prayer_hijri_date_readable'] = None
            
    elif prayer_times_data and 'error' in prayer_times_data:
        context['prayer_times_error'] = f"{prayer_times_data['error']}: {prayer_times_data.get('detail', '')}"
        context['prayer_times_json'] = json.dumps({})
        print(f"Error passed to template for prayer times: {context['prayer_times_error']}")
    else:
        context['prayer_times_error'] = "Failed to load prayer times or unexpected response format."
        context['prayer_times_json'] = json.dumps({})
        print(f"Unexpected prayer_times_data structure: {prayer_times_data}")

    # ... (rest of your context for Daily Inspiration, etc.)
    return render(request, 'core/home.html', context)

async def translate_view(request): # Make view asynchronous
    if request.method == 'POST':
        text_to_translate = request.POST.get('text')
        target_language = request.POST.get('target_lang', 'id')
        
        # Call the async translation function
        translated_text = await translate_text_with_gemini_api(text_to_translate, target_language)
        
        return JsonResponse({'translated_text': translated_text, 'status': 'success'})
    return JsonResponse({'error': 'Invalid request method', 'status': 'error'}, status=405)