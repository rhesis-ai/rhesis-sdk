import functools
import requests
from typing import Optional, Dict, Any, Callable, TypeVar, cast, Type
from rhesis.client import Client
from datetime import datetime
import logging

T = TypeVar("T")

logger = logging.getLogger(__name__)


def handle_http_errors(func: Callable[..., T]) -> Callable[..., Optional[T]]:
    """Decorator to handle HTTP errors in API requests."""
    @functools.wraps(func)
    def wrapper(self_or_cls, *args: Any, **kwargs: Any) -> Optional[T]:
        try:
            return func(self_or_cls, *args, **kwargs)
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error occurred: {e}")
            logger.error(f"Response content: {e.response.content.decode()}")
            logger.error(f"Request URL: {e.response.request.url}")
            logger.error(f"Request method: {e.response.request.method}")
            logger.error(f"Request headers: {e.response.request.headers}")
            if e.response.request.body:
                logger.error(f"Request body: {e.response.request.body.decode()}")
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

    endpoint: str
    fields: Dict[str, Any]

    def __init__(self, **fields: Any) -> None:
        """Initialize the entity with given fields.

        Args:
            **fields: Arbitrary keyword arguments representing entity fields.
        """
        self.fields = fields
        self.client = Client()
        self.headers = {
            "Authorization": f"Bearer {self.client.api_key}",
            "Content-Type": "application/json",
        }

    @handle_http_errors
    def save(self) -> Optional[Dict[str, Any]]:
        """Save the entity to the database."""
        try:
            # Use all fields except 'id' for the request body
            data = {k: v for k, v in self.fields.items() if k != 'id'}
            
            if "id" in self.fields:
                # Update existing entity
                url = f"{self.client.get_url(self.endpoint)}/{self.fields['id']}/"
                try:
                    response = requests.put(
                        url,
                        json=data,
                        headers=self.headers,
                    )
                    if response.status_code == 200:
                        return response.json()
                    response.raise_for_status()
                except requests.exceptions.RequestException:
                    raise
            else:
                # Create new entity
                url = f"{self.client.get_url(self.endpoint)}/"
                response = requests.post(
                    url,
                    json=data,
                    headers=self.headers,
                )
                if response.status_code == 200:
                    return response.json()
                response.raise_for_status()
            return None
        except requests.exceptions.HTTPError:
            return None

    @handle_http_errors
    def delete(self, record_id: str) -> bool:
        """Delete the entity from the database."""
        try:
            url = f"{self.client.get_url(self.endpoint)}/{record_id}/"
            response = requests.delete(
                url,
                headers=self.headers,
            )
            return response.status_code in [200, 204]
        except requests.exceptions.HTTPError:
            return False

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
    @handle_http_errors
    def exists(cls, record_id: str) -> bool:
        """Check if an entity exists."""
        client = Client()
        headers = {
            "Authorization": f"Bearer {client.api_key}",
            "Content-Type": "application/json",
        }
        url = f"{client.get_url(cls.endpoint)}/{record_id}/"
        logger.debug(f"GET request to {url} for exists check")
        response = requests.get(
            url,
            headers=headers,
        )
        return response.status_code == 200

    @classmethod
    @handle_http_errors
    def all(cls, **kwargs: Any) -> Optional[list[Any]]:
        """Retrieve all records from the API."""
        client = Client()
        headers = {
            "Authorization": f"Bearer {client.api_key}",
            "Content-Type": "application/json",
        }
        url = f"{client.get_url(cls.endpoint)}/"
        
        try:
            response = requests.get(
                url,
                params=kwargs,
                headers=headers,
            )
            if response.status_code == 200:
                result = response.json()
                if not isinstance(result, list):
                    result = [result] if result else []
                return cast(list[Any], result)
            response.raise_for_status()
        except requests.exceptions.RequestException:
            raise
        
        return None

    @handle_http_errors
    def first(cls, **kwargs: Any) -> Optional[Dict[str, Any]]:
        """Retrieve the first record matching the query parameters."""
        records = cls.all(**kwargs)
        return records[0] if records else None

    @classmethod
    @handle_http_errors
    def from_id(cls, record_id: str) -> Optional["BaseEntity"]:
        """Create an entity instance from a record ID."""
        client = Client()
        headers = {
            "Authorization": f"Bearer {client.api_key}",
            "Content-Type": "application/json",
        }
        url = f"{client.get_url(cls.endpoint)}/{record_id}/"
        logger.debug(f"GET request to {url} for from_id")
        response = requests.get(
            url,
            headers=headers,
        )
        response.raise_for_status()
        return cls(**response.json())

    def update(self) -> None:
        """Update entity in database."""
        if not self.exists(self.fields["id"]):
            raise ValueError(
                f"Cannot update {self.__class__.__name__}: "
                f"entity with id {self.fields['id']} does not exist"
            )

    @handle_http_errors
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
