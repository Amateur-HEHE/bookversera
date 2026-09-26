
from backend.openlibrary_api import (
    search_books,
    get_work_details,
    get_description,
    get_subjects,
    get_books_by_subject
)

# =========================================================
# SECTION 1: TEST BOOK SEARCH
# =========================================================

print("\nTesting book search...")

books = search_books("Harry Potter", limit=5)

for i, book in enumerate(books, start=1):
    print(i, book.get("title", "Unknown title"))

# =========================================================
# SECTION 2: TEST BOOK DETAILS
# =========================================================

if books:
    work_key = books[0].get("key", "")
    details = get_work_details(work_key)

    print("\nTesting book details...")
    print("Title:", details.get("title", "Unknown"))

    # =====================================================
    # SECTION 3: TEST DESCRIPTION
    # =====================================================

    description = get_description(details)
    print("\nDescription:")
    print(description[:300] if description else "No description found")

    # =====================================================
    # SECTION 4: TEST SUBJECTS
    # =====================================================

    subjects = get_subjects(details)

    print("\nSubjects:")
    for subject in subjects[:5]:
        print("-", subject)

# =========================================================
# SECTION 5: TEST SUBJECT SEARCH
# =========================================================

print("\nTesting subject search...")

related_books = get_books_by_subject("fantasy", limit=5)

for i, book in enumerate(related_books, start=1):
    print(i, book.get("title", "Unknown title"))

print("\nAll tests completed!")