# ================ Importy ================
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from datetime import datetime

# ================ Konfiguracja bazy danych i ORM ================
engine = create_engine('sqlite:///library.db', echo=True)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

# ================ Definicje Modeli ================
class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True)
    title = Column(String(250), nullable=False)
    author = Column(String(250), nullable=False)
    isbn = Column(String(100), unique=True)

    # Definicja relacji z tabelą 'Borrowing'
    borrowings = relationship('Borrowing', back_populates='book')

    def __repr__(self):
        return f"Book title: '{self.title}', author: '{self.author}', ISBN: '{self.isbn}'"

class Borrowing(Base):
    __tablename__ = 'borrowings'

    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey('books.id'))
    borrowed_by = Column(String(250))
    borrowed_date = Column(Date)
    returned_date = Column(Date, nullable=True)

    # Utworzenie odniesienia zwrotnego do 'Book'
    book = relationship('Book', back_populates='borrowings')

    def __repr__(self):
        return f"Borrowing book_id: {self.book_id}, borrowed_by: '{self.borrowed_by}', borrowed_date: '{self.borrowed_date}', returned_date: '{self.returned_date}'"

# Tworzenie tabel w bazie danych
Base.metadata.create_all(engine)

#================ Funkcje operacji CRUD dla książek ==================

# Dodanie nowej książki (CREATE)
def add_book(session):
    try:
        title = input("Enter book title: ")
        author = input("Enter author name: ")
        isbn = input("Enter ISBN: ")

        existing_book = session.query(Book).filter(Book.isbn == isbn).first()
        if existing_book:
            print("A book with this ISBN already exists.")
            return

        new_book = Book(title=title, author=author, isbn=isbn)
        session.add(new_book)
        session.commit()
        print("Book added successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Wyświetlenie wszystkich książek (SELECT)
def list_books(session):
    try:
        books = session.query(Book).all()
        for book in books:
            print(book)
    except Exception as e:
        print(f"An error occurred: {e}")

# Aktualizacja informacji o książce (UPDATE)
def update_book(session):
    try:
        isbn = input("Enter ISBN of the book to update: ")
        book = session.query(Book).filter(Book.isbn == isbn).first()
        if book:
            new_title = input("Enter new title (leave blank to skip): ")
            new_author = input("Enter new author name (leave blank to skip): ")
            if new_title:
                book.title = new_title
            if new_author:
                book.author = new_author
            session.commit()
            print("Book updated successfully.")
        else:
            print("Book not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Usuwanie książki (DELETE)
def delete_book(session):
    try:
        isbn = input("Enter ISBN of the book to delete: ")
        book = session.query(Book).filter(Book.isbn == isbn).first()
        if book:
            confirm = input(f"Are you sure you want to delete the book '{book.title}'? (yes/no): ")
            if confirm.lower() == 'yes':
                session.delete(book)
                session.commit()
                print("Book deleted successfully.")
            else:
                print("Deletion cancelled.")
        else:
            print("Book not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


#================ Funkcje operacji CRUD dla wypożyczeń ==================

# Wypożyczenie książki (CREATE)
def borrow_book(session):
    try:
        isbn = input("Enter ISBN of the book to borrow: ")
        book = session.query(Book).filter(Book.isbn == isbn).first()
        if book:
            borrowed_by = input("Enter the name of the borrower: ")
            borrowed_date = input("Enter borrowed date (YYYY-MM-DD): ")
            try:
                new_borrowing = Borrowing(book_id=book.id, borrowed_by=borrowed_by, borrowed_date=datetime.strptime(borrowed_date, '%Y-%m-%d'))
                session.add(new_borrowing)
                session.commit()
                print("Book borrowed successfully.")
            except ValueError:
                print("Invalid date format. Please use YYYY-MM-DD.")
        else:
            print("Book not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Zwrot książki (UPDATE)
def return_book(session):
    try:
        isbn = input("Enter ISBN of the book to return: ")
        borrowing = session.query(Borrowing).join(Book).filter(Book.isbn == isbn, Borrowing.returned_date.is_(None)).first()
        if borrowing:
            borrowing.returned_date = datetime.now()
            session.commit()
            print("Book returned successfully.")
        else:
            print("Book not found or already returned.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Aktualizacja informacji o wypożyczeniu (UPDATE)
def update_borrowing(session):
    try:
        borrowing_id = input("Enter borrowing ID to update: ")
        borrowing = session.query(Borrowing).filter(Borrowing.id == borrowing_id).first()
        if borrowing:
            new_borrowed_by = input("Enter new borrower name (leave blank to skip): ")
            new_borrowed_date = input("Enter new borrowed date (YYYY-MM-DD, leave blank to skip): ")
            new_returned_date = input("Enter new returned date (YYYY-MM-DD, leave blank to skip): ")

            if new_borrowed_by:
                borrowing.borrowed_by = new_borrowed_by
            if new_borrowed_date:
                try:
                    borrowing.borrowed_date = datetime.strptime(new_borrowed_date, '%Y-%m-%d')
                except ValueError:
                    print("Invalid date format. Please use YYYY-MM-DD.")
            if new_returned_date:
                try:
                    borrowing.returned_date = datetime.strptime(new_returned_date, '%Y-%m-%d')
                except ValueError:
                    print("Invalid date format. Please use YYYY-MM-DD.")

            session.commit()
            print("Borrowing updated successfully.")
        else:
            print("Borrowing not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Usuwanie wypożyczenia (DELETE)
def delete_borrowing(session):
    try:
        borrowing_id = input("Enter borrowing ID to delete: ")
        result = session.query(Borrowing).filter(Borrowing.id == borrowing_id).delete()
        session.commit()
        print("Borrowing deleted successfully." if result else "Borrowing not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Wyświetlenie wszystkich wypożyczeń (SELECT)
def list_borrowings(session):
    try:
        borrowings = session.query(Borrowing).all()
        for borrowing in borrowings:
            print(borrowing)
    except Exception as e:
        print(f"An error occurred: {e}")


# ================ Przykłady Join ================
# Wyświetlenie aktywnych wypożyczeń (INNER JOIN)
def list_active_borrowings(session):
    try:
        join_query = session.query(Book, Borrowing).join(Borrowing, Book.id == Borrowing.book_id).filter(Borrowing.returned_date.is_(None))
        for book, borrowing in join_query:
            print(f"Book: {book.title}, Borrowed by: {borrowing.borrowed_by}, Date: {borrowing.borrowed_date}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Wyświetlenie książek wraz z informacjami o wypożyczeniach (LEFT JOIN)
def list_books_with_borrowings(session):
    try:
        join_query = session.query(Book, Borrowing).outerjoin(Borrowing, Book.id == Borrowing.book_id)
        for book, borrowing in join_query:
            borrowing_info = f"Borrowed by: {borrowing.borrowed_by}, Date: {borrowing.borrowed_date}" if borrowing else "Not borrowed"
            print(f"Book: {book.title}, {borrowing_info}")
    except Exception as e:
        print(f"An error occurred: {e}")

#================ Główny interfejs użytkownika CLI ==================

def main_menu():
    print("\n--- Library Management System ---")
    print("1. List all books")
    print("2. Add a new book")
    print("3. Update a book")
    print("4. Delete a book")
    print("5. List all borrowings")
    print("6. Borrow a book")
    print("7. Return a book")
    print("8. List active borrowings")
    print("9. List books with their borrowings")
    print("0. Exit")
    choice = input("Enter choice: ")
    return choice

def run(session):
    while True:
        choice = main_menu()
        if choice == "1":
            list_books(session)
        elif choice == "2":
            add_book(session)
        elif choice == "3":
            update_book(session)
        elif choice == "4":
            delete_book(session)
        elif choice == "5":
            list_borrowings(session)
        elif choice == "6":
            borrow_book(session)
        elif choice == "7":
            return_book(session)
        elif choice == "8":
            list_active_borrowings(session)
        elif choice == "9":
            list_books_with_borrowings(session)
        elif choice == "0":
            print("Exiting the program.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    session = Session()
    run(session)
