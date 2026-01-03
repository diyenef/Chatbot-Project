# Chatbot Project (Django scaffold)

This repository contains a minimal Django project skeleton to get started quickly.

Quick start (PowerShell on Windows):

1. Create and activate a virtual environment:

```powershell
python -m venv .\venv
.\venv\Scripts\Activate.ps1
```

2. Upgrade pip and install dependencies:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

3. Run migrations and start the development server:

```powershell
python manage.py migrate
python manage.py runserver
```

4. Create a superuser (optional, to access admin):

```powershell
python manage.py createsuperuser
```

Files added:
- `manage.py` — Django CLI entrypoint
- `chatbot_project/` — project package (settings, urls, wsgi, asgi)
- `core/` — a tiny example app with a home page
- `templates/` — templates, including `core/index.html`
- `requirements.txt` — dependencies

API endpoints
 - POST /api/chat/ — Send a user message. JSON body: {"message": "..."}. Requires authentication (login). Returns {ok, reply, tokens} or 402 when out of tokens.
 - POST /api/tokens/add/ — Add tokens to the authenticated user's profile. JSON body: {"amount": 10}. Returns {ok, tokens}.
 - GET  /api/messages/?limit=N — Return recent chat messages for the authenticated user. Returns {ok, messages: [{role, content, created_at}, ...]}.

Pages
 - /signup/ — Sign up page
 - /chat/ — Chat UI (React-based, fetches /api/messages/ on load)
 - /profile/ — Profile & token balance
 - /buy/ — Mock buy tokens form (no real payment provider)

Local development (PowerShell)

1. Create and activate a virtual environment (recommended):

```powershell
python -m venv .\venv
.\venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

3. Run migrations and start dev server:

```powershell
python manage.py migrate
python manage.py runserver
```

4. Create a superuser for admin access (optional):

```powershell
python manage.py createsuperuser
```

Notes:
 - The chat UI is a quick prototype using React via CDN and Babel. For production, convert it to a built React app (Vite) and serve the built assets.
 - The Gemini integration is currently a stub in `core/services/gemini.py`. Provide API keys and endpoint details to enable real responses.
 - The Gemini integration is implemented in `core/services/gemini.py` and will use the following Django settings:
	 - `GEMINI_API_KEY` (set from environment; do NOT commit secrets)
	 - `GEMINI_API_URL` (the Gemini HTTP endpoint)

Example (PowerShell) — set the environment variables for the current session before running the server:

```powershell
$env:GEMINI_API_KEY = 'YOUR_API_KEY_HERE'
$env:GEMINI_API_URL = 'https://api.your-gemini-provider.example/v1/generate'
python manage.py runserver
```

The `call_gemini(prompt)` adapter is permissive and attempts to extract a text reply from several common JSON response shapes. If the API call fails at runtime the server will fall back to the internal simple bot reply and log the error.


Notes:
- Replace `SECRET_KEY` in production (set `DJANGO_SECRET_KEY` env variable instead).
- This scaffold uses SQLite for convenience.
