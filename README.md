# TinyURL - URL Shortener Service

A simple, fast URL shortening service built with Flask and SQLite.

## Features

- **Shorten URLs**: Convert long URLs into short, shareable links
- **Custom Short Codes**: Create memorable custom short codes (e.g., `/my-link`)
- **Click Tracking**: Track how many times each short URL has been clicked
- **Duplicate Detection**: Automatically returns existing short URL for duplicate submissions
- **Modern UI**: Clean, responsive web interface
- **REST API**: Full API for programmatic access

## Quick Start

### Prerequisites

- Python 3.8+
- pip

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python app.py
```

The server will start at `http://localhost:5000`.

## API Reference

### Create Short URL

```http
POST /api/shorten
Content-Type: application/json

{
    "url": "https://example.com/very/long/url",
    "custom_code": "my-link"  // optional
}
```

**Response:**
```json
{
    "short_url": "http://localhost:5000/abc123",
    "short_code": "abc123",
    "original_url": "https://example.com/very/long/url",
    "is_existing": false
}
```

### Get URL Statistics

```http
GET /api/stats/{short_code}
```

**Response:**
```json
{
    "short_code": "abc123",
    "original_url": "https://example.com/very/long/url",
    "created_at": "2024-01-15 10:30:00",
    "clicks": 42
}
```

### List Recent URLs

```http
GET /api/urls
```

Returns the 50 most recently created short URLs.

### Redirect

```http
GET /{short_code}
```

Redirects to the original URL and increments the click counter.

## Configuration

Environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `5000` | Server port |
| `DATABASE_PATH` | `urls.db` | SQLite database file path |
| `BASE_URL` | `http://localhost:5000` | Base URL for generated short links |

## Project Structure

```
├── app.py              # Flask application
├── requirements.txt    # Python dependencies
├── urls.db            # SQLite database (created on first run)
├── templates/
│   ├── index.html     # Main page
│   └── 404.html       # 404 error page
└── README.md
```

## License

MIT
