import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from backend.openlibrary_api import (
    search_books,
    get_work_details,
    get_description,
    get_subjects,
    get_books_by_subject
)


# =========================================================
# SECTION 1: COLLECTION FILTER
# =========================================================

collection_words = [
    "novels",
    "complete works",
    "collected works",
    "selected works",
    "anthology",
    "omnibus",
    "box set"
]


# =========================================================
# SECTION 2: LIVE BOOK SEARCH
# =========================================================

def search_and_select_book(query):

    books = search_books(
        query,
        limit=20
    )

    if not books:
        return []

    results = []

    for book in books[:10]:

        title = book.get(
            "title",
            "Unknown title"
        )

        authors = book.get(
            "author_name",
            []
        )

        author = (
            authors[0]
            if authors
            else "Unknown author"
        )

        year = book.get(
            "first_publish_year",
            "Unknown year"
        )

        cover_id = book.get(
            "cover_i"
        )

        cover_url = ""

        if cover_id:

            cover_url = (
                "https://covers.openlibrary.org/"
                f"b/id/{cover_id}-M.jpg"
            )

        results.append({

            "Title": title,

            "Author": author,

            "Year": year,

            "Work ID": book.get(
                "key",
                ""
            ),

            "Cover": cover_url
        })

    return results


# =========================================================
# SECTION 3: LIVE RECOMMENDATION ENGINE
# =========================================================

def get_live_recommendations(
    selected_title,
    selected_author,
    work_key,
    number=5
):

    # -----------------------------------------------------
    # STEP 1: Get selected book details
    # -----------------------------------------------------

    work_data = get_work_details(
        work_key
    )

    if not work_data:
        return pd.DataFrame()


    # -----------------------------------------------------
    # STEP 2: Get description and subjects
    # -----------------------------------------------------

    description = get_description(
        work_data
    )

    book_subjects = get_subjects(
        work_data,
        limit=20
    )


    # -----------------------------------------------------
    # STEP 3: Find candidate books
    # -----------------------------------------------------

    candidate_books = []

    # Use the first 5 subjects to find related books
    for subject in book_subjects[:5]:

        works = get_books_by_subject(
            subject,
            limit=15
        )

        for work in works:

            title = work.get(
                "title",
                ""
            )

            work_id = work.get(
                "key",
                ""
            )

            authors_data = work.get(
                "authors",
                []
            )

            author = ""

            if authors_data:

                author = authors_data[0].get(
                    "name",
                    ""
                )

            if title:

                candidate_books.append({

                    "Title": title,

                    "Author": author,

                    "Work ID": work_id
                })


    # -----------------------------------------------------
    # STEP 4: Remove duplicates and collections
    # -----------------------------------------------------

    unique_books = {}

    for book in candidate_books:

        title = book["Title"]

        if not title:
            continue


        # Don't recommend the selected book
        if (
            title.lower()
            == selected_title.lower()
        ):
            continue


        title_lower = title.lower()


        # Remove collection / combined works
        if any(
            word in title_lower
            for word in collection_words
        ):
            continue


        # Dictionary automatically removes duplicates
        unique_books[title_lower] = book


    candidate_books = list(
        unique_books.values()
    )


    # -----------------------------------------------------
    # STEP 5: Get detailed information
    # for each candidate
    # -----------------------------------------------------

    enriched_candidates = []

    for book in candidate_books:

        work_id = book["Work ID"]

        if not work_id.startswith(
            "/works/"
        ):
            continue


        candidate_data = get_work_details(
            work_id
        )

        if not candidate_data:
            continue


        candidate_description = get_description(
            candidate_data
        )

        candidate_subjects = get_subjects(
            candidate_data,
            limit=20
        )


        # -------------------------------------------------
        # Get candidate cover
        # -------------------------------------------------

        cover_url = ""

        covers = candidate_data.get(
            "covers",
            []
        )

        if covers:

            cover_url = (
                "https://covers.openlibrary.org/"
                f"b/id/{covers[0]}-M.jpg"
            )


        enriched_candidates.append({

            "Title":
                book["Title"],

            "Author":
                book["Author"],

            "Year":
                candidate_data.get(
                    "first_publish_year",
                    ""
                ),

            "Cover":
                cover_url,

            "Subjects":
                " ".join(
                    candidate_subjects
                ),

            "Description":
                candidate_description,

            "Work ID":
                work_id
        })


    # -----------------------------------------------------
    # STEP 6: Check whether candidates exist
    # -----------------------------------------------------

    if not enriched_candidates:

        return pd.DataFrame()


    live_df = pd.DataFrame(
        enriched_candidates
    )


    # =====================================================
    # SECTION 7: CREATE TEXT FOR TF-IDF
    # =====================================================

    # Candidate book text
    live_df["Tags"] = (

        live_df["Title"].fillna("") +
        " " +

        live_df["Author"].fillna("") +
        " " +

        live_df["Subjects"].fillna("") +
        " " +

        live_df["Description"].fillna("")
    )


    # Selected book text
    selected_tags = (

        selected_title +
        " " +

        selected_author +
        " " +

        " ".join(book_subjects) +
        " " +

        str(description)
    )


    # =====================================================
    # SECTION 8: COMBINE SELECTED BOOK + CANDIDATES
    # =====================================================

    all_tags = pd.concat(

        [

            pd.Series(
                [selected_tags]
            ),

            live_df["Tags"]

        ],

        ignore_index=True
    )


    # =====================================================
    # SECTION 9: TF-IDF
    # =====================================================

    vectorizer = TfidfVectorizer(
        stop_words="english"
    )

    tfidf_matrix = vectorizer.fit_transform(
        all_tags
    )


    # =====================================================
    # SECTION 10: COSINE SIMILARITY
    # =====================================================

    similarity_scores = cosine_similarity(

        tfidf_matrix[0:1],

        tfidf_matrix[1:]

    )[0]


    live_df["Similarity"] = (
        similarity_scores
    )


    # =====================================================
    # SECTION 11: REMOVE VERY WEAK MATCHES
    # =====================================================

    live_df = live_df[
        live_df["Similarity"] >= 0.05
    ]


    # =====================================================
    # SECTION 12: SORT BY SIMILARITY
    # =====================================================

    live_df = live_df.sort_values(

        "Similarity",

        ascending=False
    )


    # =====================================================
    # SECTION 13: RETURN TOP RECOMMENDATIONS
    # =====================================================

    return live_df[

        [
            "Title",
            "Author",
            "Year",
            "Cover",
            "Work ID",
            "Similarity"
        ]

    ].head(

        number

    ).reset_index(

        drop=True
    )


# =========================================================
# SECTION 14: MAIN RECOMMENDATION FUNCTION
# =========================================================

def recommend_book(
    work_key,
    title,
    author
):

    return {

        "Title":
            title,

        "Author":
            author,

        "Live":
            get_live_recommendations(

                title,

                author,

                work_key
            )
    }


# =========================================================
# SECTION 15: TEST MODE
# =========================================================

if __name__ == "__main__":

    query = input(
        "\nEnter a book title: "
    ).strip()


    # -----------------------------------------------------
    # Search Open Library
    # -----------------------------------------------------

    results = search_and_select_book(
        query
    )


    if not results:

        print(
            "\nBook not found."
        )

        exit()


    # -----------------------------------------------------
    # Display search results
    # -----------------------------------------------------

    print(
        "\nSearch results:"
    )

    for i, book in enumerate(
        results,
        start=1
    ):

        print(

            f"{i}. "
            f"{book['Title']} — "
            f"{book['Author']} "
            f"({book['Year']})"

        )


    # -----------------------------------------------------
    # Select a book
    # -----------------------------------------------------

    while True:

        try:

            choice = int(
                input(
                    "\nChoose a book number: "
                )
            )


            if (
                1 <= choice <= len(results)
            ):

                break


            print(
                "Please enter a valid number."
            )


        except ValueError:

            print(
                "Please enter a number."
            )


    selected = results[
        choice - 1
    ]


    print(
        "\nSelected:",
        selected["Title"]
    )


    # -----------------------------------------------------
    # Generate recommendations
    # -----------------------------------------------------

    recommendations = recommend_book(

        selected["Work ID"],

        selected["Title"],

        selected["Author"]
    )


    # -----------------------------------------------------
    # Display recommendations
    # -----------------------------------------------------

    print(
        "\nLIVE AI RECOMMENDATIONS"
    )

    print(
        "-" * 60
    )


    live = recommendations[
        "Live"
    ]


    if live.empty:

        print(
            "No similar books were found."
        )

    else:

        for _, book in live.iterrows():

            print(

                f"- {book['Title']} — "
                f"{book['Author']} "
                f"({book['Similarity']:.3f})"

            )