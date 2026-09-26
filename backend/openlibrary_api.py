import requests
from urllib.parse import quote

# =========================================================
# SECTION 1: SEARCH BOOKS
# =========================================================

def search_books(title, limit=20):
    url = "https://openlibrary.org/search.json"
    params = {
        "title": title,
        "limit": limit
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=10
        )
        response.raise_for_status()
        return response.json().get("docs", [])

    except requests.RequestException:
        print("Could not connect to Open Library.")
        return []

# =========================================================
# SECTION 2: GET BOOK DETAILS
# =========================================================

def get_work_details(work_key):
    if not work_key or not work_key.startswith("/works/"):
        return {}

    url = f"https://openlibrary.org{work_key}.json"

    try:
        response = requests.get(
            url,
            timeout=10
        )
        response.raise_for_status()
        return response.json()

    except requests.RequestException:
        return {}

# =========================================================
# SECTION 3: GET DESCRIPTION
# =========================================================

def get_description(work_data):
    description = work_data.get("description", "")

    if isinstance(description, dict):
        description = description.get("value", "")

    return description or ""

# =========================================================
# SECTION 4: GET SUBJECTS
# =========================================================

def get_subjects(work_data, limit=20):
    subjects = work_data.get("subjects", [])
    return subjects[:limit]

# =========================================================
# SECTION 5: GET BOOKS BY SUBJECT
# =========================================================

def get_books_by_subject(subject, limit=10):
    subject_url = (
        "https://openlibrary.org/subjects/"
        + quote(subject)
        + ".json"
    )

    try:
        response = requests.get(
            subject_url,
            params={"limit": limit},
            timeout=10
        )
        response.raise_for_status()

        return response.json().get("works", [])

    except requests.RequestException:
        return []

# =========================================================
# SECTION 6: GET COVER URL
# =========================================================

def get_cover_url(book):
    cover_id = book.get("cover_i")

    if cover_id:
        return (
            f"https://covers.openlibrary.org/"
            f"b/id/{cover_id}-M.jpg"
        )

    return ""

# =========================================================
# SECTION 7: FORMAT SEARCH / SUBJECT BOOK
# =========================================================

def format_book(book):
    authors = book.get("author_name", [])

    author = (
        authors[0]
        if authors
        else "Unknown author"
    )

    return {
        "Title": book.get(
            "title",
            "Unknown title"
        ),
        "Author": author,
        "Year": book.get(
            "first_publish_year",
            "Unknown year"
        ),
        "Work ID": book.get(
            "key",
            ""
        ),
        "Cover": get_cover_url(book)
    }

# =========================================================
# SECTION 8: GET HOMEPAGE BOOKS BY SUBJECT
# =========================================================

def get_homepage_books(subject, limit=10):
    books = get_books_by_subject(
        subject,
        limit=limit
    )

    results = []

    for book in books:
        authors = book.get("authors", [])

        author = "Unknown author"

        if authors:
            author = authors[0].get(
                "name",
                "Unknown author"
            )

        work_id = book.get(
            "key",
            ""
        )

        cover_id = book.get(
            "cover_id"
        )

        cover_url = ""

        if cover_id:
            cover_url = (
                f"https://covers.openlibrary.org/"
                f"b/id/{cover_id}-M.jpg"
            )

        results.append({
            "Title": book.get(
                "title",
                "Unknown title"
            ),
            "Author": author,
            "Year": book.get(
                "first_publish_year",
                "Unknown year"
            ),
            "Work ID": work_id,
            "Cover": cover_url
        })

    return results