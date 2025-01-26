import functools
import requests
from typing import Optional, Dict, Any, Callable, TypeVar, cast, Type
from rhesis.client import Client
from datetime import datetime

T = TypeVar("T")


def handle_http_errors(func: Callable[..., T]) -> Callable[..., Optional[T]]:
    """Decorator to handle HTTP errors in API requests.

    Args:
        func: The function to wrap.

    Returns:
        wrapper: The wrapped function that handles HTTP errors.
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Optional[T]:
        try:
            return func(*args, **kwargs)
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error occurred: {e}")
            return None

    return wrapper


class BaseEntity:
    """Base class for API entity interactions.

    This class provides basic CRUD operations for interacting with REST API endpoints.
    It handles authentication and common HTTP operations.

    Attributes:
        client (Client): The Rhesis API client instance
        headers (Dict[str, str]): HTTP headers for API requests.
    """

    endpoint: str = ""

    def __init__(self, **fields: Any) -> None:
        """Initialize the entity with given fields.

        Args:
            **fields: Arbitrary keyword arguments representing entity fields.
        """
        self.client = Client()
        self.fields = fields
        self.headers = {
            "Authorization": f"Bearer {self.client.api_key}",
            "Content-Type": "application/json",
        }

    @classmethod
    def exists(cls, record_id: str) -> bool:
        """Check if a record exists in the API.

        Args:
            record_id (str): The ID of the record to check.

        Returns:
            bool: True if the record exists, False otherwise.
        """
        client = Client()
        headers = {
            "Authorization": f"Bearer {client.api_key}",
            "Content-Type": "application/json",
        }
        response = requests.get(
            client.get_url(f"{cls.endpoint}/{record_id}"), headers=headers
        )
        return response.status_code == 200

    @handle_http_errors
    def save(self) -> Dict[str, Any]:
        """Save the current entity to the API.

        If the entity has an ID, updates the existing record.
        Otherwise, creates a new record.

        Returns:
            Dict[str, Any]: The saved record data from the API response.
        """
        if "id" in self.fields:
            response = requests.put(
                self.client.get_url(f"{self.endpoint}/{self.fields['id']}"),
                json=self.fields,
                headers=self.headers,
            )
        else:
            response = requests.post(
                self.client.get_url(self.endpoint),
                json=self.fields,
                headers=self.headers,
            )
        response.raise_for_status()
        return cast(Dict[str, Any], response.json())

    @handle_http_errors
    def delete(self, record_id: str) -> None:
        """Delete a record from the API.

        Args:
            record_id (str): The ID of the record to delete.
        """
        response = requests.delete(
            self.client.get_url(f"{self.endpoint}/{record_id}"), headers=self.headers
        )
        response.raise_for_status()

    @handle_http_errors
    def fetch(self) -> None:
        """Fetch the current entity's data from the API and update local fields."""
        response = requests.get(
            self.client.get_url(f"{self.endpoint}/{self.fields['id']}"),
            headers=self.headers,
        )
        response.raise_for_status()
        self.fields.update(response.json())

    @handle_http_errors
    def to_record(self) -> Dict[str, Any]:
        """Convert the entity to a dictionary representation.

        Returns:
            Dict[str, Any]: The entity's fields as a dictionary.
        """
        return self.fields

    @classmethod
    def all(cls, **kwargs: Any) -> list[Any]:
        """Retrieve all records from the API."""
        client = Client()
        headers = {
            "Authorization": f"Bearer {client.api_key}",
            "Content-Type": "application/json",
        }
        response = requests.get(
            client.get_url(cls.endpoint), params=kwargs, headers=headers
        )
        response.raise_for_status()
        return cast(list[Any], response.json())

    @classmethod
    def first(cls, **kwargs: Any) -> Optional[Dict[str, Any]]:
        """Retrieve the first record matching the query parameters."""
        records = cls.all(**kwargs)
        return records[0] if records else None

    @classmethod
    def from_id(
        cls: Type["BaseEntity"], record_id: str, fetch: bool = True
    ) -> "BaseEntity":
        """Create an entity instance from a record ID."""
        instance = cls(**{"id": record_id})
        if fetch:
            instance.fetch()
        return instance

    def update(self) -> None:
        """Update entity in database."""
        if not self.exists(self.fields["id"]):
            raise ValueError(
                f"Cannot update {self.__class__.__name__}: "
                f"entity with id {self.fields['id']} does not exist"
            )

    @classmethod
    def get_by_id(cls, id: str) -> Dict[str, Any]:
        """Get entity by id."""
        entity_dict = cls.fields.get(id)
        if entity_dict is None:
            raise ValueError(
                f"Cannot get {cls.__name__}: "
                f"entity with id {id} does not exist in database"
            )
        return cast(Dict[str, Any], entity_dict)

    def _validate_update(self) -> None:
        """Validate entity before update."""
        if not (
            isinstance(self.fields.get("created_at"), datetime)
            and isinstance(self.fields.get("updated_at"), datetime)
        ):
            raise ValueError(
                f"Cannot update {self.__class__.__name__}: "
                f"created_at and updated_at must be datetime objects"
            )
