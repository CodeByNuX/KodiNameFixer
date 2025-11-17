import os
import re
import requests
from dotenv import load_dotenv
from pathlib import Path

# 
# Load TMDB Bearer Token from .env
# 
load_dotenv()
TMDB_BEARER = os.getenv("TMDB_BEARER")

if not TMDB_BEARER:
    print("ERROR: TMDB_BEARER not found in .env file.")
    print("Add this to your .env file:\nTMDB_BEARER=YOUR_TOKEN_HERE\n")
    exit(1)

HEADERS = {
    "accept": "application/json",
    "Authorization": f"Bearer {TMDB_BEARER}"
}

TMDB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"

# 
# USER CONFIG — CHANGE YOUR MOVIE DIRECTORY HERE
# 
MOVIE_DIR = Path(r"Z:\Movies")   # <-- Update this

# Allowed video extensions
VIDEO_EXT = [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv"]

# 
# Clean raw filenames to create better TMDB search queries
# 
def clean_title(filename_stem: str) -> str:
    title = filename_stem.replace(".", " ").replace("_", " ")

    # Remove known junk tags
    junk_tags = [
        r"\b1080p\b", r"\b720p\b", r"\b2160p\b", r"\b4k\b",
        r"\bBluRay\b", r"\bBRRip\b", r"\bWEBRip\b", r"\bWEB\b",
        r"\bHDRip\b", r"\bH264\b", r"\bH265\b", r"\bX264\b", r"\bX265\b",
        r"\bDVDRip\b", r"\bDVD\b", r"\bCAM\b", r"\bTS\b", r"\bR5\b",
        r"\bYIFY\b", r"\bRARBG\b", r"\bREMASTERED\b", r"\bUNCUT\b",
        r"\bEXTENDED\b", r"\bDIRECTORS?\s*CUT\b", r"\bLIMITED\b",
        r"\bREMUX\b", r"\bPROPER\b", r"\bREPACK\b"
    ]

    for pattern in junk_tags:
        title = re.sub(pattern, "", title, flags=re.IGNORECASE)

    # Remove parentheses unless it's a year
    title = re.sub(r"\((?!\d{4}\)).*?\)", "", title)

    # Remove release group suffixes: " - RARBG"
    title = re.sub(r"-\s*\w+$", "", title)

    # Clean trailing hyphens or underscores
    title = re.sub(r"[-_]+$", "", title)

    # Collapse multiple spaces
    title = re.sub(r"\s{2,}", " ", title).strip()

    return title

# 
# TMDB Search with multiple-choice selection
# 
def tmdb_search_movie(query: str):
    params = {
        "query": query,
        "include_adult": "false",
        "language": "en-US",
        "page": 1,
    }

    response = requests.get(TMDB_SEARCH_URL, headers=HEADERS, params=params)

    if response.status_code != 200:
        print(f"TMDB API error: {response.status_code}")
        return None

    data = response.json()
    results = data.get("results", [])

    # Fallback — retry without years/numbers
    if not results and any(char.isdigit() for char in query):
        stripped = re.sub(r"\d{4}", "", query)
        params["query"] = stripped.strip()
        response = requests.get(TMDB_SEARCH_URL, headers=HEADERS, params=params)
        data = response.json()
        results = data.get("results", [])

    if not results:
        return None

    print("\nPossible matches:")
    choices = []
    for i, movie in enumerate(results[:8], 1):
        title = movie.get("title", "Unknown")
        year = movie.get("release_date", "")[:4] if movie.get("release_date") else "????"
        overview = movie.get("overview", "")
        print(f"{i}) {title} ({year})")
        if overview:
            print(f"    {overview[:100]}{'...' if len(overview)>100 else ''}")
        choices.append(movie)

    while True:
        choice = input("Select movie number or S to skip: ").strip().lower()
        if choice == "s":
            return None
        if choice.isdigit() and 1 <= int(choice) <= len(choices):
            return choices[int(choice)-1]
        print("Invalid choice. Try again.")

# 
# Build Kodi-compliant filename, Windows-safe
# 
def build_new_filename(movie, extension: str) -> str:
    title = movie.get("title", "").strip()
    release_date = movie.get("release_date", "")
    year = release_date[:4] if release_date else "0000"

    # Windows-illegal characters
    title = re.sub(r'[<>:"/\\|?*]', ' ', title)
    title = re.sub(r"\s{2,}", " ", title).strip()

    return f"{title} ({year}){extension}"

# 
# Main Renamer Logic (Recursive)
# 
def main():
    print(f"\nScanning folder recursively: {MOVIE_DIR}\n")

    for file in MOVIE_DIR.rglob("*"):
        if not file.is_file():
            continue

        if file.suffix.lower() not in VIDEO_EXT:
            continue

        print("\n--------------------------------------")
        print(f"Found file: {file.name}")

        # 
        # AUTO-SKIP — if file already follows Kodi naming exactly
        # 
        kodi_pattern = r"^(.+)\s\((\d{4})\)\.[a-zA-Z0-9]+$"
        if re.match(kodi_pattern, file.name):
            print("Already in Kodi naming format — auto-skip.")
            continue

        cleaned_title = clean_title(file.stem)
        print(f"Search title guess: '{cleaned_title}'")

        movie = tmdb_search_movie(cleaned_title)

        if not movie:
            print("SKIPPED — No match chosen or found.")
            continue

        # Build expected Kodi-compliant filename
        expected_name = build_new_filename(movie, file.suffix)

        # Auto-skip if already correctly named
        if file.name == expected_name:
            print("Already correctly named — automatically skipping.")
            continue

        new_name = expected_name
        new_path = file.with_name(new_name)

        print(f"\nOld: {file.name}")
        print(f"New: {new_name}")

        confirm = input("Rename? [Y]es / [S]kip: ").lower().strip()
        if confirm == "y":

            # Skip if target already exists
            if new_path.exists():
                print("File with that name already exists — skipping.")
                continue

            # Try rename, skip if locked or OS error
            try:
                file.rename(new_path)
                print("Renamed successfully!")

            except PermissionError:
                print("File is locked or in use — skipping.")

            except OSError as e:
                print(f"OS error: {e} — skipping.")

        else:
            print("Skipped.")

# 
# Entry Point
# 
if __name__ == "__main__":
    main()
