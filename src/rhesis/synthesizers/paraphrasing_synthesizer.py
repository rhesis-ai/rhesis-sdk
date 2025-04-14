from typing import List, Dict, Any, cast
import json
from rhesis.synthesizers.base import TestSetSynthesizer
from rhesis.entities.test_set import TestSet
import uuid


class ParaphrasingSynthesizer(TestSetSynthesizer):
    """A synthesizer that generates paraphrased versions of existing test cases."""

    def __init__(self, test_set: TestSet, batch_size: int = 5):
        """
        Initialize the ParaphrasingSynthesizer.

        Args:
            test_set: The original test set to paraphrase
            batch_size: Maximum number of prompts to process in a single LLM call
        """
        super().__init__(batch_size=batch_size)
        self.test_set = test_set
        self.num_paraphrases: int = 2  # Default value, can be overridden in generate()

    def _parse_paraphrases(self, content: str) -> List[Dict[str, str]]:
        """Parse the LLM response content into a list of paraphrased versions."""
        parsed = json.loads(content)

        if isinstance(parsed, list):
            return [
                {"prompt": {"content": p.get("content", ""), "language_code": "en"}}
                for p in parsed
            ]

        raise ValueError(f"Unexpected response format: {content}")

    def _generate_paraphrases(self, test: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate paraphrased versions of a single test.

        Args:
            test: The original test to paraphrase

        Returns:
            List[Dict[str, Any]]: List of paraphrased versions, exactly num_paraphrases in length
        """
        formatted_prompt = self.system_prompt.render(
            original_prompt=test["prompt"]["content"], num_paraphrases=self.num_paraphrases
        )

        messages = [
            {"role": "system", "content": formatted_prompt},
            {"role": "user", "content": "Generate the paraphrased versions now."},
        ]

        content = self._create_llm_completion(
            messages, temperature=0.8, max_tokens=4000, top_p=0.95
        )

        paraphrases = self._parse_json_response(content)

        # Ensure we get exactly num_paraphrases results
        if len(paraphrases) < self.num_paraphrases:
            for attempt in range(2):
                additional_content = self._create_llm_completion(
                    messages, temperature=0.9, max_tokens=4000, top_p=0.95
                )
                additional_paraphrases = self._parse_json_response(additional_content)
                paraphrases.extend(additional_paraphrases)

                if len(paraphrases) >= self.num_paraphrases:
                    break

            if len(paraphrases) < self.num_paraphrases:
                raise ValueError(
                    f"LLM returned {len(paraphrases)} paraphrases, expected {self.num_paraphrases}"
                )

        # Take exactly num_paraphrases results
        paraphrases = paraphrases[: self.num_paraphrases]

        return [
            {
                "prompt": {
                    "content": p["prompt"]["content"] if isinstance(p["prompt"], dict) else p["content"],
                    "language_code": "en"
                },
                "behavior": test["behavior"],
                "category": test["category"],
                "topic": test["topic"],
                "metadata": {
                    "generated_by": "ParaphrasingSynthesizer",
                    "original_test_id": test.get("id", "unknown"),
                    "is_paraphrase": True,
                    "original_content": test["prompt"]["content"] if isinstance(test["prompt"], dict) else test["prompt"],
                },
            }
            for p in paraphrases
        ]

    def generate(self, **kwargs: Any) -> TestSet:
        """
        Generate paraphrased versions of all tests in the test set.

        Args:
            **kwargs: Supports:
                num_paraphrases (int): Number of paraphrases to generate per test. Defaults to 2.

        Returns:
            TestSet: A TestSet containing original tests plus their paraphrased versions,
                    with paraphrases appearing immediately after their original test
        """
        self.num_paraphrases = kwargs.get("num_paraphrases", 2)
        original_tests = self.test_set.to_dict()
        all_tests = []

        def process_test(test: Dict[str, Any]) -> None:
            """Process a single test and its paraphrases."""
            all_tests.append(test)  # Add original
            paraphrases = self._generate_paraphrases(test)  # Generate paraphrases
            all_tests.extend(paraphrases)  # Add paraphrases

        # Use the base class's progress bar
        self._process_with_progress(
            original_tests,
            process_test,
            desc=f"Generating {self.num_paraphrases} paraphrases per test",
        )

        test_set = TestSet(
            id=str(uuid.uuid4()),
            tests=all_tests,
            metadata={
                "original_test_set_id": self.test_set.fields.get("id", "unknown"),
                "num_paraphrases": self.num_paraphrases,
                "num_original_tests": len(original_tests),
                "total_tests": len(all_tests),
                "batch_size": self.batch_size,
                "synthesizer": "ParaphrasingSynthesizer",
            },
        )

        # Set attributes based on the generated tests
        test_set.set_attributes()

        return test_set
