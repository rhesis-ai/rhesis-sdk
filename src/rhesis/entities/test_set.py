import os
import requests
import pandas as pd
from datetime import datetime
from typing import Any, cast, Optional, Union

from rhesis.entities import BaseEntity
from rhesis.entities.base_entity import handle_http_errors


class TestSet(BaseEntity):
    """A class representing a test set in the API.

    This class provides functionality to interact with test sets, including
    retrieving prompts, loading data in different formats, and downloading test sets.

    Examples:
        Create and load a test set:
        >>> test_set = TestSet(id='123')
        >>> df = test_set.load(format='pandas')  # Load as pandas DataFrame
        >>> prompts = test_set.load(format='dict')  # Load as list of dictionaries

        Get prompts directly:
        >>> prompts = test_set.get_prompts()
        >>> print(f"Number of prompts: {len(prompts)}")

        Download test set to local file:
        >>> # Download to current directory as CSV
        >>> test_set.download()
        >>> # Download to specific path as different format
        >>> test_set.download(format='json', path='data/my_test_set.json')
    """

    #: :no-index: The API endpoint for test sets
    endpoint = "test_sets"

    #: :no-index: Cached list of prompts for the test set
    prompts: Optional[list[Any]] = None

    def __init__(self, **fields: Any) -> None:
        """Initialize a TestSet instance.

        Args:
            **fields: Arbitrary keyword arguments representing test set fields.
        """
        super().__init__(**fields)

    @handle_http_errors
    def get_prompts(self, **kwargs: Any) -> list[Any]:
        """Retrieve prompts for the test set from the API.

        If prompts are already cached, returns the cached version.
        Otherwise, fetches prompts from the API.

        Args:
            **kwargs: Additional query parameters for the API request.

        Returns:
            list[Any]: A list of prompts associated with the test set.
        """
        if self.prompts is not None:
            return self.prompts

        response = requests.get(
            self.client.get_url(f"{self.endpoint}/{self.fields['id']}/prompts"),
            params=kwargs,
            headers=self.headers,
        )
        response.raise_for_status()
        return cast(list[Any], response.json())

    @handle_http_errors
    def load(self, format: str = "pandas") -> Union[pd.DataFrame, list[Any]]:
        """Load and format the test set prompts.

        Fetches the test set data and its prompts, then returns them in the specified format.

        Args:
            format (str, optional): The desired output format.
                Options are "pandas", "parquet", or "dict". Defaults to "pandas".

        Returns:
            Union[pd.DataFrame, list[Any]]: The prompts in the specified format.
                Returns a pandas DataFrame if format="pandas",
                writes to parquet file if format="parquet",
                or a list of dictionaries if format="dict".

        Raises:
            ValueError: If an invalid format is specified.
            ImportError: If pyarrow is not installed when using parquet format.
        """
        self.fetch()
        prompts = self.get_prompts()
        if prompts is None:
            raise ValueError("Failed to fetch prompts")
        self.prompts = prompts

        if format == "pandas":
            return pd.DataFrame(self.prompts)
        elif format == "parquet":
            try:
                import pyarrow  # noqa: F401
            except ImportError:
                raise ImportError(
                    "pyarrow is required for parquet support. "
                    "Install it with: pip install pyarrow"
                )
            df = pd.DataFrame(self.prompts)
            file_path = f"test_set_{self.fields['id']}.parquet"
            df.to_parquet(file_path)
            return df
        elif format == "dict":
            return self.prompts
        else:
            raise ValueError(f"Invalid format: {format}")

    @handle_http_errors
    def download(self, format: str = "csv", path: str = ".") -> bool:
        """Download the test set to a local file.

        Downloads the test set data and saves it to the specified path
        in the requested format.

        Args:
            format: The file format to download. Defaults to "csv".
            path: The path where the file should be saved.
                Can be a directory or a full file path. Defaults to current directory.

        Returns:
            bool: True if the download was successful.

        Note:
            The file will be named 'test_set_{id}.{format}' where id is the test set ID.
        """
        response = requests.get(
            self.client.get_url(f"{self.endpoint}/{self.fields['id']}/download"),
            headers=self.headers,
        )
        response.raise_for_status()

        # Get the directory path
        dir_path = os.path.dirname(path)

        # Only try to create directory if there's actually a directory path
        if dir_path:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)

        file_path = os.path.join(path, f"test_set_{self.fields['id']}.{format}")
        with open(file_path, "wb") as f:
            f.write(response.content)
        return True

    def update(self) -> None:
        if not self.exists(self.fields["id"]):
            raise ValueError(
                f"Cannot update test set: test set with id {self.fields['id']} does not exist"
            )

    def _validate_update(self) -> None:
        if not isinstance(self.fields.get("created_at"), datetime):
            raise ValueError(
                "Cannot update test set: created_at must be a datetime object"
            )

    @classmethod
    def all(cls, **kwargs: Any) -> list[Any]:
        """Retrieve all records from the API.

        Args:
            **kwargs: Additional query parameters for the API request.

        Returns:
            list[Any]: List of test set records.
        """
        response = requests.get(
            cls.client.get_url(cls.endpoint),
            params=kwargs,
            headers=cls.headers,
        )
        response.raise_for_status()
        return cast(list[Any], response.json())
