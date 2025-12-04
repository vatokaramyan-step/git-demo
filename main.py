
import json
import sys
import csv
import requests  # pyright: ignore[reportMissingModuleSource]

# -------------------------
# CLASS BOOK
# -------------------------
class Book:
    counter = 0

    def __init__(self, title, author, genre, publication_year, book_id=None):
        self.title = title
        self.author = author
        self.genre = genre
        self.publication_year = publication_year

        if book_id is not None:
            self.book_id = book_id
        else:
            Book.counter += 1
            self.book_id = Book.counter

    def __str__(self):
        return f"ID: {self.book_id} | Title: {self.title} | Author: {self.author} | Genre: {self.genre} | Year: {self.publication_year}"

    def to_dict(self):
        return {
            'book_id': self.book_id,
            'title': self.title,
            'author': self.author,
            'genre': self.genre,
            'publication_year': self.publication_year
        }


# -------------------------
# CLASS LIBRARY
# -------------------------
class Library:
    def __init__(self):
        self.books = []

    def add_book(self, title, author, genre, publication_year):
        title = title.strip()
        author = author.strip()
        if not title or not author:
            print("❌ Cannot add book with empty Title or Author.")
            return False

        for book in self.books:
            if book.title.lower() == title.lower() and \
               book.author.lower() == author.lower():
                print(f"❌ Book '{title}' by '{author}' already exists in the library.")
                return False

        new_book = Book(title, author, genre, publication_year)
        self.books.append(new_book)
        print(f"✅ Book '{title}' added to the library (ID: {new_book.book_id}).")
        return True

    def add_book_by_isbn(self, isbn):
        isbn = isbn.strip()
        if not isbn:
            print("❌ ISBN cannot be empty!")
            return
        url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            print(f"❌ Error fetching data from Open Library: {e}")
            data = {}

        book_data = data.get(f"ISBN:{isbn}")

        if book_data:
            title = book_data.get("title", "").strip()
            authors = book_data.get("authors", [])
            author = authors[0]["name"].strip() if authors else ""
            year = book_data.get("publish_date", "").split()[-1]
            try:
                year = int(year)
            except:
                year = 0

            print(f"✅ Found book: {title} by {author}, Year: {year}")
            self.add_book(title, author, "", year)

        else:
            print("❌ Book not found with this ISBN. Please enter manually.")
            title = input("Enter Title: ").strip()
            author = input("Enter Author: ").strip()
            genre = input("Enter Genre: ").strip()
            year_input = input("Enter Publication Year: ").strip()
            try:
                year = int(year_input)
            except:
                year = 0
            self.add_book(title, author, genre, year)

    def view_all_books(self):
        if not self.books:
            print("❌ Library is empty.")
            return

        print("\n--- All Books ---")
        for book in self.books:
            print(book)

    def search_book(self, search_term):
        found_books = []
        s = search_term.lower()

        for book in self.books:
            if (s in book.title.lower() or
                s in book.author.lower() or
                s in book.genre.lower()):
                found_books.append(book)

        if not found_books:
            print(f"\n❌ Book(s) with the term '{search_term}' not found.")
        else:
            print(f"\n✅ Found {len(found_books)} book(s):")
            for book in found_books:
                print("-" * 40)
                print(book)
                print("-" * 40)

    def remove_book(self, book_id):
        try:
            target_id = int(book_id)
        except ValueError:
            print("❌ ID must be a number.")
            return

        for book in self.books:
            if book.book_id == target_id:
                self.books.remove(book)
                print(f"✅ Book '{book.title}' removed.")
                return

        print(f"❌ No book found with ID {book_id}.")

    def update_book(self, book_id):
        try:
            target_id = int(book_id)
        except ValueError:
            print("❌ ID must be a number.")
            return

        for book in self.books:
            if book.book_id == target_id:
                print("\n--- Update Book ---")
                new_title = input(f"Enter new title (Old: '{book.title}'): ").strip()
                new_author = input(f"Enter new author (Old: '{book.author}'): ").strip()
                new_genre = input(f"Enter new genre (Old: '{book.genre}'): ").strip()
                new_year = input(f"Enter new publication year (Old: '{book.publication_year}'): ").strip()

                if new_title:
                    book.title = new_title
                if new_author:
                    book.author = new_author
                if new_genre:
                    book.genre = new_genre

                if new_year:
                    try:
                        new_year = int(new_year)
                        if 0 <= new_year <= 2025:
                            book.publication_year = new_year
                        else:
                            print("⚠️ Invalid year (0–2025 only).")
                    except ValueError:
                        print("⚠️ Year not updated: invalid number.")

                print(f"✅ Book ID {book_id} updated.")
                return

        print(f"❌ No book found with ID {book_id}.")

    def save_data(self):
        try:
            with open("library_data.json", "w", encoding='utf-8') as f:
                json.dump([b.to_dict() for b in self.books], f, indent=4)
            print("✅ Saved JSON.")
        except Exception as e:
            print(f"❌ Error saving JSON: {e}")

    def save_data_csv(self):
        try:
            with open("library_data.csv", "w", newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['book_id', 'title', 'author', 'genre', 'publication_year'])
                writer.writeheader()
                writer.writerows([b.to_dict() for b in self.books])
            print("✅ Saved CSV.")
        except Exception as e:
            print(f"❌ Error saving CSV: {e}")

    def save_all_data(self):
        self.save_data()
        self.save_data_csv()

    def load_data(self):
        try:
            with open("library_data.json", "r", encoding='utf-8') as f:
                data = json.load(f)

            self.books = [Book(**d) for d in data]

            if self.books:
                Book.counter = max(int(b.book_id) for b in self.books)

            print("✅ Loaded data.")
        except FileNotFoundError:
            print("No saved library found, starting empty.")
        except Exception as e:
            print(f"❌ Load error: {e}")


# -------------------------
# MAIN (CLI)
# -------------------------
def main():
    library = Library()
    library.load_data()

    while True:
        print("\n=== 📚 BOOK LIBRARY MANAGER 📚 ===")
        print("1️⃣  Add Book")
        print("2️⃣  View All Books")
        print("3️⃣  Search Book")
        print("4️⃣  Remove Book")
        print("5️⃣  Update Book")
        print("6️⃣  Save Data (JSON + CSV)")
        print("7️⃣  Load Data (JSON)")
        print("8️⃣  Exit")
        choice = input("👉 Choose an option (1-8): ").strip()

        if choice == '1':
            print("\n📘 ADD NEW BOOK")

            while True:
                use_isbn = input("Do you want to add by ISBN? (y/n): ").strip().lower()

                if use_isbn == "y":
                    isbn = input("Enter ISBN: ").strip()
                    library.add_book_by_isbn(isbn)
                    library.save_all_data()
                    break

                elif use_isbn == "n":
                    title = input("Enter Title: ").strip()
                    author = input("Enter Author: ").strip()
                    genre = input("Enter Genre: ").strip()
                    year = input("Enter Publication Year: ").strip()

                    if not title or not author or not genre or not year:
                        print("❌ Title, Author, and Year cannot be empty!")
                    else:
                        try:
                            year = int(year)
                            library.add_book(title, author, genre, year)
                            library.save_all_data()
                        except ValueError:
                            print("❌ Invalid year!")
                    break

                else:
                    print("❌ Please choose one of: 'y' or 'n'.")
                    retry = input("Try again (y/n): ").strip().lower()
                    if retry == "n":
                        break

                    if retry not in ("y", "n"):
                        print("⚠️ Invalid again — returning to main menu...")
                        break

                    use_isbn = retry
                    continue

        elif choice == '2':
            library.view_all_books()

        elif choice == '3':
            term = input("Enter search term: ").strip()
            library.search_book(term)

        elif choice == '4':
            book_id = input("Enter Book ID: ").strip()
            library.remove_book(book_id)
            library.save_all_data()

        elif choice == '5':
            book_id = input("Enter Book ID: ").strip()
            library.update_book(book_id)
            library.save_all_data()

        elif choice == '6':
            library.save_all_data()

        elif choice == '7':
            library.load_data()

        elif choice == '8':
            print("\n👋 Goodbye!")
            sys.exit()

        else:
            print("❌ Invalid choice. Enter a number 1–8.")


if __name__ == "__main__":
    main()
