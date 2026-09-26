import pandas as pd
import requests
import time

# Load our cleaned Open Library dataset
df = pd.read_csv("openlibrary_books.csv")

# Remove duplicate titles
df = df.drop_duplicates(subset="Title").reset_index(drop=True)

# Lists to store new information
descriptions = []
subjects = []

print("Starting enrichment...")
print("Books to process:", len(df))

for i, row in df.iterrows():

    work_id = row["Book ID"]
    url = f"https://openlibrary.org{work_id}.json"

    try:
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()

            # Get description
            description = data.get("description", "")

            # Sometimes description is a dictionary
            if isinstance(description, dict):
                description = description.get("value", "")

            # Get subjects
            book_subjects = data.get("subjects", [])

            # Keep only the first 20 subjects
            book_subjects = book_subjects[:20]

            descriptions.append(description)
            subjects.append(", ".join(book_subjects))

        else:
            descriptions.append("")
            subjects.append("")

    except Exception as e:
        print("Error:", row["Title"])
        descriptions.append("")
        subjects.append("")

    # Progress
    if (i + 1) % 25 == 0:
        print(f"Processed {i + 1}/{len(df)}")

    # Small delay between requests
    time.sleep(0.2)


# Add new columns
df["Description"] = descriptions
df["Subjects"] = subjects

# Save enriched dataset
df.to_csv("enriched_books.csv", index=False)

print("\nEnrichment complete!")
print("Saved as: enriched_books.csv")

print("\nNew columns:")
print(df.columns)