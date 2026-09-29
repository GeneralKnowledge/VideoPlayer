#!/usr/bin/env python3
"""
Fictional embed URL helper for local demos.

Uses a placeholder host so this never points at a real streaming service.
Pair with the TMDB search webpage to look up titles you care about.
"""

from __future__ import annotations

import argparse

# Placeholder only — not a real video host.
BASE_URL = "https://embed.example.invalid"


def movie_url(tmdb_id: str) -> str:
    return f"{BASE_URL}/movie/{tmdb_id}"


def tv_url(tmdb_id: str, season: int, episode: int) -> str:
    return f"{BASE_URL}/tv/{tmdb_id}/{season}/{episode}"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build fictional embed URLs from TMDB IDs."
    )
    subparsers = parser.add_subparsers(dest="type", required=True)

    movie_parser = subparsers.add_parser("movie", help="Movie embed URL")
    movie_parser.add_argument("id", help="TMDB movie ID")

    tv_parser = subparsers.add_parser("tv", help="TV episode embed URL")
    tv_parser.add_argument("id", help="TMDB TV show ID")
    tv_parser.add_argument("season", type=int, help="Season number")
    tv_parser.add_argument("episode", type=int, help="Episode number")

    args = parser.parse_args()

    if args.type == "movie":
        print(movie_url(args.id))
    else:
        print(tv_url(args.id, args.season, args.episode))


if __name__ == "__main__":
    main()
