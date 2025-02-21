from abc import ABC, abstractmethod
from typing import Any, List, Dict
import json
from pathlib import Path
from tqdm.auto import tqdm
from jinja2 import Template
from rhesis.services import LLMService
from rhesis.entities.test_set import TestSet


class TestSetSynthesizer(ABC):
    """Base class for all test set synthesizers."""

    def __init__(self, batch_size: int = 5):
        """
        Initialize the base synthesizer.

        Args:
            batch_size: Maximum number of items to process in a single LLM call
        """
        self.batch_size = batch_size
        self.llm_service = LLMService()
        self.system_prompt = self._load_prompt_template()

    def _load_prompt_template(self) -> Template:
        """Load the prompt template from assets directory."""
        # Convert camel case to snake case
        class_name = self.__class__.__name__
        snake_case = "".join(
            ["_" + c.lower() if c.isupper() else c.lower() for c in class_name]
        ).lstrip("_")
        prompt_path = Path(__file__).parent / "assets" / f"{snake_case}.md"
        with open(prompt_path, "r") as f:
            return Template(f.read())

    def _parse_json_response(self, content: str) -> List[Dict[str, Any]]:
        """Parse the LLM JSON response into a list of dictionaries."""
        try:
            parsed = json.loads(content)

            # Handle response wrapped in a field
            if isinstance(parsed, dict) and len(parsed) == 1:
                possible_list = list(parsed.values())[0]
                if isinstance(possible_list, list):
                    return possible_list

            # Handle direct list response
            if isinstance(parsed, list):
                return parsed

            # Handle single item response
            if isinstance(parsed, dict):
                return [parsed]

            raise ValueError("Unexpected response structure")
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON response: {str(e)}")

    def _create_llm_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.8,
        max_tokens: int = 4000,
        top_p: float = 0.95,
    ) -> str:
        """Create an LLM completion and return the content."""
        response: Dict[str, Any] = self.llm_service.create_completion(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
        )
        # Ensure we're returning a string
        return str(response["choices"][0]["message"]["content"])

    def _process_with_progress(
        self,
        items: List[Any],
        process_func: Any,
        desc: str = "Processing",
    ) -> List[Any]:
        """Process items with a progress bar."""
        results = []
        with tqdm(total=len(items), desc=desc) as pbar:
            for item in items:
                result = process_func(item)
                if isinstance(result, list):
                    results.extend(result)
                else:
                    results.append(result)
                pbar.update(1)
        return results

    @abstractmethod
    def generate(self, **kwargs: Any) -> TestSet:
        """
        Generate a test set based on the synthesizer's implementation.

        Args:
            **kwargs: Additional keyword arguments for test set generation

        Returns:
            TestSet: A TestSet entity containing the generated test cases
        """
        pass
