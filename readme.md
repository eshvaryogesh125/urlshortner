# URL Shortener

A simple URL shortener API built with FastAPI, SQLAlchemy, and SQLite.

## Features

- Create short URLs for long links.
- Optional custom alias support.
- Redirect short codes to original URLs.
- Background click counting for each redirect.
- Added In-memory caching
- Rate limiting on creation and redirect endpoints.

## Prerequisites

- Python 3.11+
- `pip`
- A `.env` file with:
  - `DATABASE_URL` (for example: `sqlite:///./urls.db`)
  - `BASE_URL` (for example: `http://localhost:8000`)
  - `MACHINE_ID` (optional; defaults to `1`; reserved for future Docker/container deployments)

## Installation

1. Clone the repository.
2. Create a virtual environment:
   - Windows: `python -m venv venv`
   - Unix/macOS: `python3 -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/macOS: `source venv/bin/activate`
4. Install dependencies:
   - `pip install fastapi sqlalchemy pydantic uvicorn python-dotenv slowapi`

## Running the app

1. Start the server:
   - `uvicorn main:app --reload`
2. Open the API at:
   - `http://127.0.0.1:8000`

## API Endpoints

### POST /shorten

Create a short URL.

Request body:

```json
{
  "url": "https://example.com",
  "custom_alias": "myalias"
}
```

Response example:

```json
{
  "short_url": "http://localhost:8000/myalias"
}
```

Notes:
- `custom_alias` is optional.
- If the URL already exists, the service returns the existing short URL.
- Requests are limited to `5/minute` per client.

### GET /{short_code}

Redirects to the original URL for the given short code.

Notes:
- Redirects use HTTP `302`.
- Redirect requests are rate limited to `10/minute` per client.

## Database

- `database.py` configures the SQLAlchemy engine and session.
- `models.py` defines `URL` and `Click` tables.
- Click counts are updated asynchronously in `tasks.py`.

## Project files

- `main.py`: FastAPI application and endpoint definitions.
- `models.py`: SQLAlchemy models for URLs and clicks.
- `schemas.py`: Pydantic request/response models.
- `utils.py`: URL generation, cache helpers, and DB helpers.
- `database.py`: Database connection setup.
- `tasks.py`: Background task for click count updates.
- `powershell_cmd.txt`: Example PowerShell commands for testing.

## Notes

- The app builds short URLs using the `BASE_URL` value from `.env`.
- If `BASE_URL` is not set, it defaults to `http://localhost:8000`.
- A simple in-memory cache is used for redirect lookups with a 10-minute TTL.
- Custom aliases must be unique.
- `MACHINE_ID` is reserved for future Docker/container deployments to support unique short-code generation across instances.
