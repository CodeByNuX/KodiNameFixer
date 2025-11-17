# KodiNameFixer

KodiNameFixer is a Python utility that scans a movie directory, looks up each title using TheMovieDB (TMDB) API, and renames the files to match official Kodi naming conventions. This ensures that Kodi can correctly identify and scrape your media library without manual intervention.

The tool is interactive: for each movie, it suggests one or more matches from TMDB. You can confirm the correct title, skip it, or allow automatic renaming when an exact match is detected.

---

## Features

- Recursively scans directories containing movie files  
- Parses filenames to extract a title guess  
- Queries TMDB using its official Search API  
- Displays a list of matching movies with release years  
- Renames files following Kodi’s official format:  
  ```
  Movie Title (Year).ext
  ```  
- Skips files that already follow the correct format  
- Skips files currently in use or locked  
- Requires a TMDB API Bearer Token (stored in `.env`)  
- Works with local and network drives  

---

## Requirements

- Python 3.9 or later  
- TMDB API Bearer Token (v4)  
- Packages:  
  - `requests`  
  - `python-dotenv`  

Install dependencies:

```bash
pip install python-dotenv requests
```

---

## TMDB API Setup

1. Create a free account at [https://www.themoviedb.org](https://www.themoviedb.org).  
2. Go to **Settings → API → Create API Key (v4)**.  
3. Copy your Bearer Token (starts with `eyJhbGci...`).  

---

## Setting Your Movie Folder Path

You must edit the movie folder path **directly inside the Python script**.

Open the script file (for example, `rename.py`) and find this line near the top:

```python
MOVIE_FOLDER = r"Z:\Movies\"
```

Change it so it points to the folder where your movies are stored. For example:

```python
MOVIE_FOLDER = r"D:\Media\Movies\"
```

or:

```python
MOVIE_FOLDER = r"/mnt/storage/Movies/"
```

This is the **only** place you need to modify the movie directory.  
The script will scan this folder (and all subfolders) automatically.

---

## Usage

Run the script:

```bash
python rename.py
```

The script will:

1. Scan the specified movie directory.  
2. Parse each movie filename into a title guess.  
3. Query TMDB for possible matches.  
4. Display a list of results for you to choose from.  
5. Ask for confirmation before renaming the file.  

Example:

```
Found file: The.Superdeep.mp4
Search title guess: "The Superdeep"

Possible matches:
1) Superdeep (2020)
   Description: ...
Select movie number or S to skip: 1

Old: The.Superdeep.mp4
New: Superdeep (2020).mp4
Rename? [Y/S]: Y
```

---

## Kodi Naming Standards

This project follows official Kodi naming guidelines:  
[https://kodi.wiki/view/Naming_video_files](https://kodi.wiki/view/Naming_video_files)

Example of proper naming:

```
Alien (1979).mp4
The Matrix (1999).mkv
John Wick (2014).avi
```

---

## Directory Scanning Rules

- Scans recursively through the movie directory.  
- Recognizes common video formats:  

  ```
  mp4, mkv, avi, mov, m4v, wmv, mpg, mpeg
  ```

- Only renames files, not folders.  

---

## Error Handling

- Files already named correctly are skipped.  
- Locked or in-use files are skipped.  
- Invalid API matches are skipped.  
- Rename failures (e.g. permission errors) are logged and ignored.  

---

## Limitations

- Handles movies only (TV shows not supported).  
- Filename readability affects detection accuracy.  
- TMDB API rate limits may apply.  
- Folders are not renamed.  

---

## Contributing

Contributions are welcome.  
Submit pull requests to improve parsing, support additional formats, or enhance automation.  

---

## License

MIT License.  
You may freely use, modify, and distribute this project.

