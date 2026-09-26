import pandas as pd

# Load our collected dataset
df = pd.read_csv("openlibrary_books.csv")

print("Shape:", df.shape)

print("\nMissing values:")
print(df.isnull().sum())

print("\nDuplicate rows:", df.duplicated().sum())

print("\nUnique titles:", df["Title"].nunique())

print("\nUnique authors:", df["Author"].nunique())

print("\nSubjects:")
print(df["Subject"].value_counts())

print("\nData types:")
print(df.dtypes)