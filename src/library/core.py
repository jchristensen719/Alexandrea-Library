"""Core functionality for the library management system."""
from dataclasses import dataclass

@dataclass
class Book:
    """Represents a book in the library."""
    isbn: str

    def __post_init__(self):
        """Validate and normalize ISBN after initialization."""
        if not self.isbn:
            raise ValueError("ISBN cannot be empty")
        # Normalize ISBN by removing hyphens
        self.isbn = self.isbn.replace("-", "")