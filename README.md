# Quran & Hadith App

A modern web application for exploring the Quran and Hadith collections, featuring prayer times, translation, and a clean, responsive UI built with Django and Tailwind CSS.

## Features
- **Quran Explorer**: Browse Surahs, view ayahs, listen to recitations, and read tafsir.
- **Hadith Browser**: Search and read hadiths from various books.
- **Prayer Times**: Daily prayer times fetched from an external API.
- **Translation**: (Mock) translation using Gemini API.
- **Modern UI**: Responsive design with Tailwind CSS and dark mode support.
- **Async Django Views**: Uses Django 4+ async views and httpx for fast API calls.

## Screenshots

### Home Page
![Home Page](Screenshot%202025-06-04%20at%2008.24.08.png)

### Prayer Times
![Prayer Times](Screenshot%202025-06-04%20at%2008.24.16.png)

### Quran Explorer
![Quran Explorer](Screenshot%202025-06-04%20at%2008.24.22.png)

### Hadith Browser
![Hadith Browser](Screenshot%202025-06-04%20at%2008.24.28.png)

### Dark Mode
![Dark Mode](Screenshot%202025-06-04%20at%2008.24.46.png)

### Mobile View
![Mobile View](Screenshot%202025-06-04%20at%2008.24.51.png)

## Tech Stack
- **Backend**: Python 3.10+, Django 5.x, async views
- **Frontend**: Tailwind CSS 3.x, PostCSS, @tailwindcss/forms
- **Database**: PostgreSQL
- **API Clients**: httpx (async), python-dotenv

## Setup Instructions

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd quran_hadits_app
```

### 2. Python Environment
- Install Python 3.10+ and PostgreSQL.
- Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```
- Install Python dependencies:
```bash
pip install django httpx python-dotenv psycopg2-binary
```

### 3. Node & Tailwind CSS
- Install Node.js (v16+ recommended).
- Install dependencies:
```bash
npm install
```
- Build Tailwind CSS:
```bash
npm run build:css
```
- For development (auto-rebuild):
```bash
npm run watch:css
```

### 4. Environment Variables
Create a `.env` file in the project root with the following variables:
```
SECRET_KEY=your-django-secret-key
DEBUG=True
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
EQURAN_API_BASE_URL=https://equran.id/api/v2
HADITH_API_BASE_URL=https://api.hadith.gading.dev
PRAYER_TIMES_API_BASE_URL=https://api.aladhan.com/v1
PRAYER_TIMES_CITY=Jakarta
PRAYER_TIMES_COUNTRY=Indonesia
PRAYER_TIMES_METHOD=5
# Optional Gemini API (mocked in this project)
GEMINI_PROJECT_ID=your-gemini-project-id
GEMINI_LOCATION=your-gemini-location
```

### 5. Database Setup
- Create a PostgreSQL database and user matching your `.env`.
- Run migrations:
```bash
python manage.py migrate
```

### 6. Run the Development Server
```bash
python manage.py runserver
```
Visit [http://localhost:8000](http://localhost:8000) in your browser.

## Project Structure
- `core/` - Main app (home, prayer times, translation)
- `quran_app/` - Quran features
- `hadith_app/` - Hadith features
- `quran_hadith_project/` - Django project settings
- `core/static/core/css/` - Tailwind CSS source and output

## External APIs
- **Quran**: [equran.id](https://equran.id/)
- **Hadith**: [api.hadith.gading.dev](https://api.hadith.gading.dev/)
- **Prayer Times**: [Aladhan](https://aladhan.com/prayer-times-api)
- **Translation**: Gemini API (mocked)

## Contributing
Pull requests are welcome! Please open an issue first to discuss major changes.

## License

This project is licensed under the [MIT License](LICENSE).