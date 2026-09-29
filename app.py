#!/usr/bin/env python3
"""TMDB search webpage with fictional embed URL helpers."""

from __future__ import annotations

import os
from typing import Any

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

from embed_urls import movie_url, tv_url

load_dotenv()

TMDB_API = "https://api.themoviedb.org/3"
TMDB_IMAGE = "https://image.tmdb.org/t/p"

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-only-secret")


def tmdb_key() -> str | None:
    key = os.getenv("TMDB_API_KEY", "").strip()
    return key or None


def tmdb_get(path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    key = tmdb_key()
    if not key:
        raise RuntimeError(
            "TMDB_API_KEY is not set. Copy .env.example to .env and add your key."
        )

    query = dict(params or {})
    query["api_key"] = key
    response = requests.get(f"{TMDB_API}{path}", params=query, timeout=15)
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, dict):
        raise RuntimeError("Unexpected TMDB response")
    return data


def poster_url(path: str | None, size: str = "w342") -> str | None:
    if not path:
        return None
    return f"{TMDB_IMAGE}/{size}{path}"


def normalize_result(item: dict[str, Any], media_type: str) -> dict[str, Any]:
    kind = item.get("media_type") or media_type
    if kind == "movie":
        title = item.get("title") or item.get("original_title") or "Untitled"
        date = item.get("release_date") or ""
        embed = movie_url(str(item["id"]))
    elif kind == "tv":
        title = item.get("name") or item.get("original_name") or "Untitled"
        date = item.get("first_air_date") or ""
        embed = tv_url(str(item["id"]), 1, 1)
    else:
        title = item.get("name") or item.get("title") or "Untitled"
        date = item.get("release_date") or item.get("first_air_date") or ""
        embed = None

    year = date[:4] if date else ""
    return {
        "id": item.get("id"),
        "media_type": kind,
        "title": title,
        "overview": item.get("overview") or "",
        "year": year,
        "rating": item.get("vote_average"),
        "poster": poster_url(item.get("poster_path")),
        "backdrop": poster_url(item.get("backdrop_path"), "w780"),
        "embed_url": embed,
    }


@app.get("/")
def index() -> str:
    return render_template(
        "index.html",
        has_api_key=bool(tmdb_key()),
    )


@app.get("/api/health")
def health() -> Any:
    return jsonify({"ok": True, "tmdb_configured": bool(tmdb_key())})


@app.get("/api/search")
def search() -> Any:
    query = (request.args.get("q") or "").strip()
    media = (request.args.get("type") or "multi").strip().lower()

    if not query:
        return jsonify({"results": [], "error": "Enter a search term."}), 400

    if not tmdb_key():
        return (
            jsonify(
                {
                    "results": [],
                    "error": "Set TMDB_API_KEY in your .env file to search.",
                }
            ),
            503,
        )

    try:
        if media == "movie":
            data = tmdb_get("/search/movie", {"query": query, "include_adult": "false"})
            results = [normalize_result(item, "movie") for item in data.get("results", [])]
        elif media == "tv":
            data = tmdb_get("/search/tv", {"query": query, "include_adult": "false"})
            results = [normalize_result(item, "tv") for item in data.get("results", [])]
        else:
            data = tmdb_get("/search/multi", {"query": query, "include_adult": "false"})
            results = [
                normalize_result(item, item.get("media_type", "movie"))
                for item in data.get("results", [])
                if item.get("media_type") in {"movie", "tv"}
            ]
    except requests.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else 502
        return jsonify({"results": [], "error": f"TMDB request failed ({status})."}), status
    except requests.RequestException:
        return jsonify({"results": [], "error": "Could not reach TMDB."}), 502
    except RuntimeError as exc:
        return jsonify({"results": [], "error": str(exc)}), 503

    return jsonify({"results": results, "query": query})


@app.get("/api/embed")
def embed() -> Any:
    media = (request.args.get("type") or "movie").strip().lower()
    tmdb_id = (request.args.get("id") or "").strip()

    if not tmdb_id.isdigit():
        return jsonify({"error": "id must be a numeric TMDB ID"}), 400

    if media == "movie":
        url = movie_url(tmdb_id)
    elif media == "tv":
        season = int(request.args.get("season") or 1)
        episode = int(request.args.get("episode") or 1)
        url = tv_url(tmdb_id, season, episode)
    else:
        return jsonify({"error": "type must be movie or tv"}), 400

    return jsonify({"url": url, "note": "Fictional demo URL only."})


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
