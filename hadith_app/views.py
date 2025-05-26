# hadith_app/views.py
import httpx # For asynchronous HTTP requests
import asyncio # For async operations
from django.shortcuts import render
from django.http import Http404
from django.conf import settings # To access API configurations

async def fetch_hadith_api_httpx(endpoint):
    """
    Asynchronous helper function to fetch data from the Hadith API using httpx.
    """
    base_url = settings.HADITH_API_BASE_URL
    if not base_url:
        print("Error: HADITH_API_BASE_URL is not configured in settings.")
        return None

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{base_url}/{endpoint}")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        print(f"HTTP error fetching from Hadith API ({e.request.url}): {e.response.status_code} - {e.response.text}")
        return None
    except httpx.RequestError as e:
        print(f"Request error fetching from Hadith API ({e.request.url}): {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred in fetch_hadith_api_httpx: {e}")
        return None


async def hadith_home_view(request): # Make view asynchronous
    books_data = []
    api_error = None
    try:
        response_data = await fetch_hadith_api_httpx("books")
        if response_data and 'data' in response_data and isinstance(response_data['data'], list):
            books_data = response_data['data']
        elif response_data: # Handle if API returns list directly
            books_data = response_data
            print("Warning: Hadith API response for books might not be in the expected {'data': [...]} format. Using raw response.")
        else:
            api_error = "Could not fetch Hadith books from API or the response was empty/invalid."
    except Exception as e:
        print(f"Error in hadith_home_view: {e}")
        api_error = "An unexpected error occurred while processing Hadith books data."

    query = request.GET.get('q_hadith_book', '')
    if query and books_data:
        books_data = [b for b in books_data if query.lower() in b.get('name', '').lower()]

    return render(request, 'hadith_app/hadith_home.html', {
        'books': books_data,
        'query': query,
        'api_error': api_error
    })


async def hadith_list_view(request, book_slug): # Make view asynchronous
    hadiths_data = []
    book_info = {}
    api_error = None
    # page = request.GET.get('page', 1) # Pagination not fully implemented here
    limit = 30 # Number of hadiths per page, increased for better view

    try:
        # The API /books/{slug}?range=1-30 returns book info and hadiths
        hadith_range = f"1-{limit}"
        response_data = await fetch_hadith_api_httpx(f"books/{book_slug}?range={hadith_range}")

        if response_data and 'data' in response_data:
            api_content = response_data['data']
            book_info = {
                'id': api_content.get('id', book_slug),
                'name': api_content.get('name', book_slug.replace('-', ' ').title()),
                'available': api_content.get('available', 0)
            }
            hadiths_data = api_content.get('hadiths', [])
            if not hadiths_data and book_info.get('available', 0) > 0 :
                 api_error = f"Successfully fetched book info for {book_info['name']}, but no Hadiths were returned for the range {hadith_range}."
            elif not hadiths_data and book_info.get('available', 0) == 0:
                 api_error = f"The book {book_info['name']} is available but currently contains no Hadiths according to the API."

        elif not response_data:
            # Attempt to fetch just book info if the ranged call failed or returned nothing
            book_info_response = await fetch_hadith_api_httpx(f"books/{book_slug}")
            if book_info_response and 'data' in book_info_response:
                api_content = book_info_response['data']
                book_info = {
                    'id': api_content.get('id', book_slug),
                    'name': api_content.get('name', book_slug.replace('-', ' ').title()),
                    'available': api_content.get('available', 0)
                }
                api_error = f"Could not fetch Hadiths for {book_info['name']}, but book information is available. The range query might have failed or returned no data."
            else:
                api_error = f"Could not fetch details for Hadith book: {book_slug}."
                book_info = {'name': book_slug.replace('-', ' ').title() + " (Error Loading)", 'id': book_slug, 'available': 'N/A'}
        else:
            api_error = "Received an unexpected response format from Hadith API."
            print(f"Unexpected Hadith API response for {book_slug}: {response_data}")


    except Exception as e:
        print(f"Error in hadith_list_view for book {book_slug}: {e}")
        api_error = f"An unexpected error occurred while processing Hadith data for {book_slug}."
        book_info = {'name': book_slug.replace('-', ' ').title() + " (Error Loading)", 'id': book_slug, 'available': 'N/A'}

    query = request.GET.get('q_hadith_text', '')
    if query and hadiths_data:
        # 'id' field in hadith data from this API often contains the Indonesian translation.
        hadiths_data = [h for h in hadiths_data if query.lower() in h.get('id', '').lower() or query.lower() in h.get('arab', '').lower()]

    return render(request, 'hadith_app/hadith_list.html', {
        'book': book_info,
        'hadiths': hadiths_data,
        'query': query,
        'api_error': api_error
    })