import requests
import pandas as pd

subjects = [
    "fiction",
    "fantasy",
    "science_fiction",
    "mystery",
    "romance",
    "history",
    "philosophy",
    "adventure"
]

books = []

for subject in subjects:

    url = f"https://openlibrary.org/subjects/{subject}.json"

    params = {
        "limit": 100
    }

    response = requests.get(url, params=params)

    print(subject, response.status_code)

    data = response.json()

    for book in data["works"]:
        books.append({
            "Title": book.get("title"),
            "Author": ", ".join(
                author["name"] for author in book.get("authors", [])
            ),
            "Year": book.get("first_publish_year"),
            "Cover ID": book.get("cover_id"),
            "Subject": subject,
            "Book ID": book.get("key")
        })


df = pd.DataFrame(books)

print("\nTotal books:", len(df))
print("\nFirst 5 books:")
print(df.head())

print("\nColumns:")
print(df.columns)

df.to_csv("openlibrary_books.csv", index=False)

print("\nDataset saved as books.csv")