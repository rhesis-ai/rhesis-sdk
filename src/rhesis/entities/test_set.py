import os
import requests
import pandas as pd
from datetime import datetime
from typing import Any, cast, Optional, Union, Dict, List
from pathlib import Path
from jinja2 import Template

from rhesis.entities import BaseEntity
from rhesis.entities.base_entity import handle_http_errors
from rhesis.utils import count_tokens
from rhesis.services.llm import LLMService


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

    #: :no-index: Cached list of tests for the test set
    tests: Optional[list[Any]] = None
    categories: Optional[list[str]] = None
    topics: Optional[list[str]] = None
    test_count: Optional[int] = None

    def __init__(self, **fields: Any) -> None:
        """Initialize a TestSet instance.

        Args:
            **fields: Arbitrary keyword arguments representing test set fields.
        """
        super().__init__(**fields)

        self.name = fields.get("name", None)
        self.description = fields.get("description", None)
        self.short_description = fields.get("short_description", None)
        self.tests = fields.get("tests", None)

    @handle_http_errors
    def get_tests(self, **kwargs: Any) -> list[Any]:
        """Retrieve tests for the test set from the API.

        If tests are already cached, returns the cached version.
        Otherwise, fetches tests from the API.

        Args:
            **kwargs: Additional query parameters for the API request.

        Returns:
            list[Any]: A list of tests associated with the test set.
        """
        if self.tests is not None:
            return self.tests

        response = requests.get(
            self.client.get_url(f"{self.endpoint}/{self.fields['id']}/tests"),
            params=kwargs,
            headers=self.headers,
        )
        response.raise_for_status()
        return cast(list[Any], response.json())

    @handle_http_errors
    def load(self, format: str = "pandas") -> Union[pd.DataFrame, list[Any]]:
        """Load and format the test set tests.

        Fetches the test set data and its tests, then returns them in the specified format.

        Args:
            format (str, optional): The desired output format.
                Options are "pandas", "parquet", or "dict". Defaults to "pandas".

        Returns:
            Union[pd.DataFrame, list[Any]]: The tests in the specified format.
                Returns a pandas DataFrame if format="pandas",
                writes to parquet file if format="parquet",
                or a list of dictionaries if format="dict".

        Raises:
            ValueError: If an invalid format is specified.
            ImportError: If pyarrow is not installed when using parquet format.
        """
        self.fetch()
        tests = self.get_tests()
        if tests is None:
            raise ValueError("Failed to fetch tests")
        self.tests = tests

        if format == "pandas":
            return pd.DataFrame(self.tests)
        elif format == "parquet":
            try:
                import pyarrow  # noqa: F401
            except ImportError:
                raise ImportError(
                    "pyarrow is required for parquet support. "
                    "Install it with: pip install pyarrow"
                )
            df = pd.DataFrame(self.tests)
            file_path = f"test_set_{self.fields['id']}.parquet"
            df.to_parquet(file_path)
            return df
        elif format == "dict":
            return self.tests
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

    def count_tokens(self, encoding_name: str = "cl100k_base") -> Dict[str, int]:
        """Count tokens for all prompts in the test set.

        Args:
            encoding_name: The name of the encoding to use. Defaults to cl100k_base
                          (used by GPT-4 and GPT-3.5-turbo)

        Returns:
            Dict[str, int]: A dictionary containing token statistics
        """
        # Ensure prompts are loaded
        if self.tests is None:
            self.get_tests()

        if not self.tests:
            return {
                "total": 0,
                "average": 0,
                "max": 0,
                "min": 0,
                "test_count": 0,
            }

        # Count tokens for each prompt's content
        token_counts = []
        for test in self.tests:
            content = test.get("content", "")
            if not isinstance(content, str):
                continue

            token_count = count_tokens(content, encoding_name)
            if token_count is not None:
                token_counts.append(token_count)

        if not token_counts:
            return {
                "total": 0,
                "average": 0,
                "max": 0,
                "min": 0,
                "test_count": 0,
            }

        return {
            "total": sum(token_counts),
            "average": int(round(sum(token_counts) / len(token_counts))),
            "max": max(token_counts),
            "min": min(token_counts),
            "test_count": len(token_counts),
        }

    def to_dict(self) -> List[Dict[str, Any]]:
        """Convert the test set tests to a list of dictionaries.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing test data
        """
        if self.tests is None:
            self.get_tests()
        if self.tests is None:  # Double-check after get_tests
            return []
        return cast(List[Dict[str, Any]], self.tests)

    def to_pandas(self) -> pd.DataFrame:
        """Convert the test set tests to a pandas DataFrame.

        Returns:
            pd.DataFrame: A DataFrame containing the test data

        Example:
            >>> test_set = TestSet(id='123')
            >>> df = test_set.to_pandas()
            >>> print(df.columns)
        """
        if self.tests is None:
            self.get_tests()
        return pd.DataFrame(self.tests)

    def to_parquet(self, path: Optional[str] = None) -> pd.DataFrame:
        """Convert the test set tests to a parquet file.

        Args:
            path: The path where the parquet file should be saved.
                 If None, uses 'test_set_{id}.parquet'

        Returns:
            pd.DataFrame: The DataFrame that was saved to parquet

        Raises:
            ImportError: If pyarrow is not installed

        Example:
            >>> test_set = TestSet(id='123')
            >>> df = test_set.to_parquet('my_test_set.parquet')
        """
        try:
            import pyarrow  # noqa: F401
        except ImportError:
            raise ImportError(
                "pyarrow is required for parquet support. "
                "Install it with: pip install pyarrow"
            )

        df = self.to_pandas()

        if path is None:
            path = f"test_set_{self.fields['id']}.parquet"

        df.to_parquet(path)
        return df

    def to_csv(self, path: Optional[str] = None) -> pd.DataFrame:
        """Convert the test set tests to a CSV file.

        Args:
            path: The path where the CSV file should be saved.
                 If None, uses 'test_set_{id}.csv'

        Returns:
            pd.DataFrame: The DataFrame that was saved to CSV

        Example:
            >>> test_set = TestSet(id='123')
            >>> df = test_set.to_csv('my_test_set.csv')
        """
        df = self.to_pandas()

        if path is None:
            path = f"test_set_{self.fields['id']}.csv"

        df.to_csv(path, index=False)
        return df

    def get_properties(self) -> Dict[str, Any]:
        """Get the test set properties including basic info and test analysis.

        Returns:
            Dict[str, Any]: A dictionary containing:
                - basic properties (name, description, short_description)
                - unique categories and topics from tests
                - total number of tests

        Example:
            >>> test_set = TestSet(id='123')
            >>> props = test_set.get_properties()
            >>> print(f"Categories: {props['categories']}")
            >>> print(f"Topics: {props['topics']}")
        """
        # Ensure tests are loaded
        if self.tests is None:
            self.get_tests()

        # Initialize sets for unique categories and topics
        categories = set()
        topics = set()

        # Extract unique categories and topics from tests
        if self.tests is not None:
            for test in self.tests:
                if isinstance(test, dict):
                    if "category" in test and test["category"]:
                        categories.add(test["category"])
                    if "topic" in test and test["topic"]:
                        topics.add(test["topic"])

        return {
            "name": self.name,
            "description": self.description,
            "short_description": self.short_description,
            "categories": sorted(list(categories)),
            "topics": sorted(list(topics)),
            "test_count": len(self.tests) if self.tests is not None else 0,
        }

    def set_attributes(self) -> None:
        """Set test set attributes using LLM based on categories and topics in tests.

        This method:
        1. Gets the unique categories and topics from tests
        2. Uses the LLM service to generate appropriate name, description, and short description
        3. Updates the test set's attributes

        Example:
            >>> test_set = TestSet(id='123')
            >>> test_set.set_attributes()
            >>> print(f"Name: {test_set.name}")
            >>> print(f"Description: {test_set.description}")
        """
        # Ensure tests are loaded
        if self.tests is None:
            self.get_tests()

        # Get unique categories and topics
        categories = set()
        topics = set()
        if self.tests is not None:
            for test in self.tests:
                if isinstance(test, dict):
                    if "category" in test and test["category"]:
                        categories.add(test["category"])
                    if "topic" in test and test["topic"]:
                        topics.add(test["topic"])

        # Load the prompt template
        prompt_path = (
            Path(__file__).parent.parent
            / "synthesizers"
            / "assets"
            / "test_set_attributes.md"
        )
        with open(prompt_path, "r") as f:
            template = Template(f.read())

        # Format the prompt
        formatted_prompt = template.render(
            topics=sorted(list(topics)), categories=sorted(list(categories))
        )

        # Create LLM service and get response
        llm_service = LLMService()
        response = llm_service.run(formatted_prompt)
        # Update test set attributes
        if isinstance(response, dict):
            self.name = response.get("name")
            self.description = response.get("description")
            self.short_description = response.get("short_description")
            self.categories = sorted(list(categories))
            self.topics = sorted(list(topics))
            self.test_count = len(self.tests) if self.tests is not None else 0
        else:
            raise ValueError("LLM response was not in the expected format")
