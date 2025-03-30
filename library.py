"""
Alexandrea Library main module.

This module provides a simplified interface to the Alexandrea Library system.
It combines functionality from both the core library implementation and
the simplified library implementation.
"""

import logging
import re
from datetime import datetime
from typing import List, Optional  # Removed Any, Dict, Set, Tuple, Union

from src.alexandrea_library.core import Book as CoreBook
from src.alexandrea_library.core import BookStatus
from src.alexandrea_library.core import Library as CoreLibrary
from src.alexandrea_library.core import Member as CoreMember

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/library.log"), logging.StreamHandler()],
)

logger = logging.getLogger("alexandrea.library")


# Custom exceptions for better error reporting
class LibraryError(Exception):
    """Base class for all library exceptions."""

    pass


class BookExistsError(LibraryError):
    """Raised when attempting to add a book that already exists."""

    pass


class InvalidISBNError(LibraryError):
    """Raised when an invalid ISBN is provided."""

    pass


class MemberExistsError(LibraryError):
    """Raised when attempting to register a member that already exists."""

    pass


class InvalidEmailError(LibraryError):
    """Raised when an invalid email is provided."""

    pass


class BookNotFoundError(LibraryError):
    """Raised when a book is not found."""

    pass


class MemberNotFoundError(LibraryError):
    """Raised when a member is not found."""

    pass


class CheckoutError(LibraryError):
    """Raised when a checkout operation fails."""

    pass


class ReturnError(LibraryError):
    """Raised when a return operation fails."""

    pass


# Simplified interface for the Alexandrea Library system
class Library:
    """
    Main interface for the Alexandrea Library system.

    This class provides a simplified interface to the library system,
    making it easier to manage books, members, and checkouts.

    Examples:
        >>> library = Library("Alexandrea Library")
        >>> book = library.add_book("The Republic", "Plato", "123456789", 380)
        >>> member = library.register_member("user123", "John Doe", "john@example.com")
        >>> library.checkout_book(member.id, book.isbn)
        True
    """

    def __init__(self, name: str):
        """
        Initialize a new library.

        Args:
            name: The name of the library
        """
        self.core_library = CoreLibrary(name)
        self.name = name
        logger.info(f"Library '{name}' initialized")

    def _validate_isbn(self, isbn: str) -> bool:
        """
        Validate ISBN format.

        Args:
            isbn: The ISBN to validate

        Returns:
            True if valid, False otherwise
        """
        # Basic ISBN-10 or ISBN-13 validation
        # ISBN-10: 10 digits, possibly with hyphens
        # ISBN-13: 13 digits, possibly with hyphens
        isbn_cleaned = isbn.replace("-", "").replace(" ", "")
        return (len(isbn_cleaned) in (10, 13) and isbn_cleaned.isdigit()) or (
            len(isbn_cleaned) == 10
            and isbn_cleaned[:-1].isdigit()
            and isbn_cleaned[-1].lower() == "x"
        )

    def _validate_email(self, email: str) -> bool:
        """
        Validate email format.

        Args:
            email: The email to validate

        Returns:
            True if valid, False otherwise
        """
        # Basic email validation using regex
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(email_pattern, email))

    def add_book(
        self, title: str, author: str, isbn: str, publication_year: int
    ) -> CoreBook:
        """
        Add a new book to the library with input validation.

        Args:
            title: The book title
            author: The book author
            isbn: The book ISBN
            publication_year: The year the book was published

        Returns:
            The newly created book

        Raises:
            InvalidISBNError: If ISBN format is invalid
            BookExistsError: If a book with the same ISBN already exists
            ValueError: If any required fields are missing or invalid
        """
        # Validate required fields
        if not title:
            logger.error("Book title cannot be empty")
            raise ValueError("Book title cannot be empty")

        if not author:
            logger.error("Book author cannot be empty")
            raise ValueError("Book author cannot be empty")

        if not isbn:
            logger.error("Book ISBN cannot be empty")
            raise ValueError("Book ISBN cannot be empty")

        # Validate ISBN format
        if not self._validate_isbn(isbn):
            logger.error(f"Invalid ISBN format: {isbn}")
            raise InvalidISBNError(f"Invalid ISBN format: {isbn}")

        # Check if book already exists
        if self.get_book(isbn):
            logger.error(f"Book with ISBN {isbn} already exists")
            raise BookExistsError(f"Book with ISBN {isbn} already exists")

        # Validate publication year
        current_year = datetime.now().year
        if (
            not isinstance(publication_year, int)
            or publication_year < 0
            or publication_year > current_year
        ):
            logger.error(f"Invalid publication year: {publication_year}")
            raise ValueError(f"Invalid publication year: {publication_year}")

        # Create and add the book
        book = CoreBook(
            title=title, author=author, isbn=isbn, publication_year=publication_year
        )

        self.core_library.add_book(book)
        logger.info(f"Book added: '{title}' by {author} (ISBN: {isbn})")
        return book

    def register_member(self, id: str, name: str, email: str) -> CoreMember:
        """
        Register a new member to the library with input validation.

        Args:
            id: The member's unique ID
            name: The member's name
            email: The member's email address

        Returns:
            The newly registered member

        Raises:
            InvalidEmailError: If email format is invalid
            MemberExistsError: If a member with the same ID already exists
            ValueError: If any required fields are missing
        """
        # Validate required fields
        if not id:
            logger.error("Member ID cannot be empty")
            raise ValueError("Member ID cannot be empty")

        if not name:
            logger.error("Member name cannot be empty")
            raise ValueError("Member name cannot be empty")

        if not email:
            logger.error("Member email cannot be empty")
            raise ValueError("Member email cannot be empty")

        # Validate email format
        if not self._validate_email(email):
            logger.error(f"Invalid email format: {email}")
            raise InvalidEmailError(f"Invalid email format: {email}")

        # Check if member already exists
        if self.get_member(id):
            logger.error(f"Member with ID {id} already exists")
            raise MemberExistsError(f"Member with ID {id} already exists")

        # Create and register the member
        member = CoreMember(id=id, name=name, email=email)

        self.core_library.register_member(member)
        logger.info(f"Member registered: {name} (ID: {id}, Email: {email})")
        return member

    def get_book(self, isbn: str) -> Optional[CoreBook]:
        """
        Get a book by its ISBN.

        Args:
            isbn: The ISBN of the book to find

        Returns:
            The book if found, None otherwise
        """
        return self.core_library.books.get(isbn)

    def get_member(self, id: str) -> Optional[CoreMember]:
        """
        Get a member by their ID.

        Args:
            id: The ID of the member to find

        Returns:
            The member if found, None otherwise
        """
        return self.core_library.members.get(id)

    def checkout_book(self, member_id: str, isbn: str) -> bool:
        """
        Check out a book to a member with error handling.

        Args:
            member_id: The ID of the member checking out the book
            isbn: The ISBN of the book to check out

        Returns:
            True if checkout was successful, False otherwise

        Raises:
            MemberNotFoundError: If the member is not found
            BookNotFoundError: If the book is not found
            CheckoutError: If the book is already checked out or other checkout issues
        """
        # Find the member
        member = self.get_member(member_id)
        if not member:
            error_msg = f"Member with ID {member_id} not found"
            logger.error(error_msg)
            raise MemberNotFoundError(error_msg)

        # Find the book
        book = self.get_book(isbn)
        if not book:
            error_msg = f"Book with ISBN {isbn} not found"
            logger.error(error_msg)
            raise BookNotFoundError(error_msg)

        # Check if book is already checked out
        if book.status == BookStatus.CHECKED_OUT:
            error_msg = f"Book '{book.title}' (ISBN: {isbn}) is already checked out"
            logger.error(error_msg)
            if book.checkout_member_id == member_id:
                error_msg += " by you"
            raise CheckoutError(error_msg)

        # Attempt to check out the book
        success = member.checkout_book(book)
        if success:
            logger.info(
                f"Book '{book.title}' (ISBN: {isbn}) checked out to member {member.name} (ID: {member_id})"
            )
            return True
        else:
            error_msg = (
                "Could not check out book. Member may have reached checkout limit."
            )
            logger.error(error_msg)
            raise CheckoutError(error_msg)

    def return_book(self, member_id: str, isbn: str) -> bool:
        """
        Return a book to the library with error handling.

        Args:
            member_id: The ID of the member returning the book
            isbn: The ISBN of the book to return

        Returns:
            True if return was successful, False otherwise

        Raises:
            MemberNotFoundError: If the member is not found
            BookNotFoundError: If the book is not found
            ReturnError: If the book is not checked out or other return issues
        """
        # Find the member
        member = self.get_member(member_id)
        if not member:
            error_msg = f"Member with ID {member_id} not found"
            logger.error(error_msg)
            raise MemberNotFoundError(error_msg)

        # Find the book
        book = self.get_book(isbn)
        if not book:
            error_msg = f"Book with ISBN {isbn} not found"
            logger.error(error_msg)
            raise BookNotFoundError(error_msg)

        # Check if book is already available
        if book.status == BookStatus.AVAILABLE:
            error_msg = f"Book '{book.title}' (ISBN: {isbn}) is not checked out"
            logger.error(error_msg)
            raise ReturnError(error_msg)

        # Check if book is checked out by this member
        if book.checkout_member_id != member_id:
            error_msg = f"Book '{book.title}' (ISBN: {isbn}) is not checked out by member {member_id}"
            logger.error(error_msg)
            raise ReturnError(error_msg)

        # Attempt to return the book
        success = member.return_book(book)
        if success:
            logger.info(
                f"Book '{book.title}' (ISBN: {isbn}) returned by member {member.name} (ID: {member_id})"
            )
            return True
        else:
            error_msg = (
                "Could not return book. It may not be checked out by this member."
            )
            logger.error(error_msg)
            raise ReturnError(error_msg)

    def search_books(self, query: Optional[str] = None, **kwargs) -> List[CoreBook]:
        """
        Search for books by various criteria.

        Args:
            query: General search query for title or author
            **kwargs: Additional search criteria including:
                title: Book title or partial title
                author: Book author or partial author
                year_from: Minimum publication year
                year_to: Maximum publication year
                status: Book status (available, checked_out, etc.)

        Returns:
            List of matching books
        """
        result_books = list(self.core_library.books.values())

        # Filter by general query (title or author)
        if query:
            query = query.lower()
            result_books = [
                book
                for book in result_books
                if query in book.title.lower() or query in book.author.lower()
            ]

        # Filter by specific criteria
        if "title" in kwargs and kwargs["title"]:
            title = kwargs["title"].lower()
            result_books = [
                book for book in result_books if title in book.title.lower()
            ]

        if "author" in kwargs and kwargs["author"]:
            author = kwargs["author"].lower()
            result_books = [
                book for book in result_books if author in book.author.lower()
            ]

        if "year_from" in kwargs and isinstance(kwargs["year_from"], int):
            result_books = [
                book
                for book in result_books
                if book.publication_year >= kwargs["year_from"]
            ]

        if "year_to" in kwargs and isinstance(kwargs["year_to"], int):
            result_books = [
                book
                for book in result_books
                if book.publication_year <= kwargs["year_to"]
            ]

        if "status" in kwargs and kwargs["status"]:
            try:
                status = BookStatus(kwargs["status"])
                result_books = [book for book in result_books if book.status == status]
            except ValueError:
                # Invalid status, ignore this filter
                logger.warning(f"Invalid book status in search: {kwargs['status']}")

        logger.info(f"Search performed. Found {len(result_books)} matching books.")
        return result_books

    def get_available_books(self) -> List[CoreBook]:
        """
        Get all available books in the library.

        Returns:
            List of all available books
        """
        return self.core_library.get_available_books()

    def get_overdue_books(self) -> List[CoreBook]:
        """
        Get all overdue books.

        Returns:
            List of all overdue books
        """
        return self.core_library.get_overdue_books()

    def remove_book(self, isbn: str) -> bool:
        """
        Remove a book from the library.

        Args:
            isbn: The ISBN of the book to remove

        Returns:
            True if the book was removed, False otherwise

        Raises:
            BookNotFoundError: If the book is not found
        """
        if not self.get_book(isbn):
            error_msg = f"Book with ISBN {isbn} not found"
            logger.error(error_msg)
            raise BookNotFoundError(error_msg)

        result = self.core_library.remove_book(isbn)
        if result:
            logger.info(f"Book with ISBN {isbn} removed from library")
        return result

    def save_to_json(self, filepath: str) -> bool:
        """
        Save library data to a JSON file.

        Args:
            filepath: Path to save the JSON file

        Returns:
            True if save was successful, False otherwise
        """
        try:
            import json
            import os

            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            # Prepare data for serialization
            data = {"name": self.name, "books": [], "members": []}

            # Serialize books
            for book in self.core_library.books.values():
                book_data = {
                    "title": book.title,
                    "author": book.author,
                    "isbn": book.isbn,
                    "publication_year": book.publication_year,
                    "status": book.status.value,
                    "checkout_member_id": book.checkout_member_id,
                }
                data["books"].append(book_data)

            # Serialize members
            for member in self.core_library.members.values():
                member_data = {
                    "id": member.id,
                    "name": member.name,
                    "email": member.email,
                    "join_date": member.join_date.isoformat(),
                    "books_checked_out": list(member.books_checked_out),
                }
                data["members"].append(member_data)

            # Write to file
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

            logger.info(f"Library data saved to {filepath}")
            return True

        except Exception as e:
            logger.error(f"Error saving library data: {e}")
            return False

    def load_from_json(self, filepath: str) -> bool:
        """
        Load library data from a JSON file.

        Args:
            filepath: Path to the JSON file

        Returns:
            True if load was successful, False otherwise
        """
        try:
            import json
            from datetime import datetime

            # Read the file
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Create a new core library
            self.name = data["name"]
            self.core_library = CoreLibrary(self.name)

            # Load books first
            for book_data in data["books"]:
                book = CoreBook(
                    title=book_data["title"],
                    author=book_data["author"],
                    isbn=book_data["isbn"],
                    publication_year=book_data["publication_year"],
                )
                book.status = BookStatus(book_data["status"])
                book.checkout_member_id = book_data["checkout_member_id"]
                self.core_library.add_book(book)

            # Then load members
            for member_data in data["members"]:
                member = CoreMember(
                    id=member_data["id"],
                    name=member_data["name"],
                    email=member_data["email"],
                )
                member.join_date = datetime.fromisoformat(member_data["join_date"])
                member.books_checked_out = set(member_data["books_checked_out"])
                self.core_library.register_member(member)

            logger.info(f"Library data loaded from {filepath}")
            return True

        except Exception as e:
            logger.error(f"Error loading library data: {e}")
            return False

    @property
    def book_count(self) -> int:
        """Get the total number of books in the library."""
        return len(self.core_library.books)

    @property
    def member_count(self) -> int:
        """Get the total number of registered members."""
        return len(self.core_library.members)


# Simplified function to create a library instance
def create_library(name: str) -> Library:
    """
    Create a new library with the given name.

    Args:
        name: The name of the library

    Returns:
        A new Library instance
    """
    return Library(name)


# Example command-line interface
def run_cli():
    """Run a simple command-line interface for the library system."""
    library = create_library("Alexandrea Main Library")
    print(f"Welcome to {library.name}")

    while True:
        print("\nOptions:")
        print("1. Add a book")
        print("2. Register a member")
        print("3. Check out a book")
        print("4. Return a book")
        print("5. Search for books")
        print("6. Save library data")
        print("7. Load library data")
        print("8. View statistics")
        print("9. Exit")

        choice = input("Enter your choice (1-9): ")

        try:
            if choice == "1":
                # Add a book
                title = input("Enter book title: ")
                author = input("Enter author name: ")
                isbn = input("Enter ISBN: ")
                year = input("Enter publication year: ")

                try:
                    book = library.add_book(title, author, isbn, int(year))
                    print(f"Book added: {book.title} (ISBN: {book.isbn})")
                except ValueError as e:
                    print(f"Error: {e}")
                except LibraryError as e:
                    print(f"Error: {e}")

            elif choice == "2":
                # Register a member
                id = input("Enter member ID: ")
                name = input("Enter member name: ")
                email = input("Enter member email: ")

                try:
                    member = library.register_member(id, name, email)
                    print(f"Member registered: {member.name} (ID: {member.id})")
                except ValueError as e:
                    print(f"Error: {e}")
                except LibraryError as e:
                    print(f"Error: {e}")

            elif choice == "3":
                # Check out a book
                member_id = input("Enter member ID: ")
                isbn = input("Enter book ISBN: ")

                try:
                    library.checkout_book(member_id, isbn)
                    print("Book checked out successfully")
                except LibraryError as e:
                    print(f"Error: {e}")

            elif choice == "4":
                # Return a book
                member_id = input("Enter member ID: ")
                isbn = input("Enter book ISBN: ")

                try:
                    library.return_book(member_id, isbn)
                    print("Book returned successfully")
                except LibraryError as e:
                    print(f"Error: {e}")

            elif choice == "5":
                # Search for books
                print("Search options:")
                print("1. General search")
                print("2. Advanced search")
                search_choice = input("Enter search type (1-2): ")

                if search_choice == "1":
                    query = input("Enter search query: ")
                    results = library.search_books(query)
                else:
                    title = input("Title (leave blank to skip): ")
                    author = input("Author (leave blank to skip): ")
                    year_from = input("Year from (leave blank to skip): ")
                    year_to = input("Year to (leave blank to skip): ")

                    kwargs = {}
                    if title:
                        kwargs["title"] = title
                    if author:
                        kwargs["author"] = author
                    if year_from:
                        kwargs["year_from"] = int(year_from)
                    if year_to:
                        kwargs["year_to"] = int(year_to)

                    results = library.search_books(**kwargs)

                if results:
                    print(f"Found {len(results)} books:")
                    for i, book in enumerate(results, 1):
                        status = (
                            "Available"
                            if book.status == BookStatus.AVAILABLE
                            else "Checked Out"
                        )
                        print(
                            f"{i}. '{book.title}' by {book.author} ({book.publication_year}) - {status}"
                        )
                else:
                    print("No books found matching the criteria.")

            elif choice == "6":
                # Save library data
                filepath = input(
                    "Enter filepath to save data (default: data/library_data.json): "
                )
                if not filepath:
                    filepath = "data/library_data.json"

                if library.save_to_json(filepath):
                    print(f"Library data saved to {filepath}")
                else:
                    print("Error saving library data")

            elif choice == "7":
                # Load library data
                filepath = input(
                    "Enter filepath to load data (default: data/library_data.json): "
                )
                if not filepath:
                    filepath = "data/library_data.json"

                if library.load_from_json(filepath):
                    print(f"Library data loaded from {filepath}")
                else:
                    print("Error loading library data")

            elif choice == "8":
                # View statistics
                print(f"Library: {library.name}")
                print(f"Total books: {library.book_count}")
                print(f"Total members: {library.member_count}")
                available = len(library.get_available_books())
                print(f"Available books: {available}")
                overdue = len(library.get_overdue_books())
                print(f"Overdue books: {overdue}")

            elif choice == "9":
                # Exit
                print("Thank you for using the Alexandrea Library System!")
                break

            else:
                print("Invalid choice. Please select a number from 1 to 9.")

        except Exception as e:
            print(f"An error occurred: {e}")

    return library


# Example usage
if __name__ == "__main__":
    # Run command-line interface
    run_cli()

    # Or create a simple demo
    # library = create_library("Alexandrea Main Library")

    # Add some books
    # try:
    #     ancient_book = library.add_book(
    #         title="Meditations",
    #         author="Marcus Aurelius",
    #         isbn="9780812968255",
    #         publication_year=180
    #     )
    #
    #     finance_book = library.add_book(
    #         title="The Intelligent Investor",
    #         author="Benjamin Graham",
    #         isbn="9780060555665",
    #         publication_year=1949
    #     )
    #
    #     # Register a member
    #     member = library.register_member(
    #         id="reader123",
    #         name="Alex Reader",
    #         email="alex@example.com"
    #     )
    #
    #     # Check out a book
    #     library.checkout_book(member.id, ancient_book.isbn)
    #
    #     # Search for books
    #     results = library.search_books("Marcus")
    #     for book in results:
    #         print(f"Found: {book.title} by {book.author}")
    #
    # except LibraryError as e:
    #     print(f"Error: {e}")
    # except Exception as e:
    #     print(f"Unexpected error: {e}")
    #     print(f"Unexpected error: {e}")
