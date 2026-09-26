from backend.recommendation_model import search_and_select_book, recommend_book

query = input("Enter a book title: ").strip()
results = search_and_select_book(query)

if not results:
    print("Book not found.")
    exit()

print("\nSearch results:")
for i, book in enumerate(results, 1):
    print(f"{i}. {book['Title']} — {book['Author']} ({book['Year']})")

choice = int(input("\nChoose a book number: "))
selected = results[choice - 1]

result = recommend_book(
    selected["Work ID"],
    selected["Title"],
    selected["Author"]
)

print(f"\nRecommendations for: {selected['Title']}")

print("\nLocal:")
if result["Local"].empty:
    print("No local recommendations available.")
else:
    for _, book in result["Local"].iterrows():
        print(f"- {book['Title']} — {book['Author']} ({book['Similarity']:.3f})")

print("\nLive:")
for _, book in result["Live"].iterrows():
    print(f"- {book['Title']} — {book['Author']} ({book['Similarity']:.3f})")