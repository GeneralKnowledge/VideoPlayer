# Cue — TMDB Search

Simple webpage to search [The Movie Database](https://www.themoviedb.org/) for movies and TV shows, then copy a **fictional** embed URL for local demos.

Embed paths use `https://embed.example.invalid` — not a real streaming host.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Add a free API key from [TMDB API settings](https://www.themoviedb.org/settings/api) to `.env`:

```env
TMDB_API_KEY=your_key_here
```

## Run the webpage

```bash
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000).

## CLI helper

```bash
python embed_urls.py movie 550
python embed_urls.py tv 1396 1 1
```

## API

| Endpoint | Description |
| --- | --- |
| `GET /api/search?q=...&type=multi\|movie\|tv` | TMDB search |
| `GET /api/embed?type=movie&id=550` | Fictional embed URL |
| `GET /api/health` | Health + whether TMDB is configured |
