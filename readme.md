# URL Shortener

A simple URL shortener API built with FastAPI and SQLAlchemy.

## Features

- Shorten long URLs to unique short codes.
- Redirect to original URLs using short codes.
- Health check endpoint.

## Installation

1. Clone the repository.
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Unix).
4. Install dependencies: `pip install fastapi sqlalchemy pydantic uvicorn`

## Usage

1. Run the application: `uvicorn main:app --reload`
2. The API will be available at `http://127.0.0.1:8000`

## API Endpoints

- **GET /health**: Health check.
- **POST /shorten**: Shorten a URL. Body: `{"url": "https://example.com"}`. Response: `{"short_url": "http://localhost:8000/ABC123"}`
- **GET /{short_code}**: Redirect to the original URL.

## Testing

Use the provided PowerShell commands in [powershell_cmd.txt](powershell_cmd.txt) to test the API.

## Database

Uses SQLite database ([database.py](database.py)). Tables defined in [models.py](models.py).

## Files

- [main.py](main.py): Main API application.
- [models.py](models.py): Database models, e.g., [`URL`](models.py).
- [schemas.py](schemas.py): Pydantic schemas.
- [utils.py](utils.py): Utility functions, e.g., [`generate_unique_code`](utils.py).
- [database.py](database.py): Database configuration.