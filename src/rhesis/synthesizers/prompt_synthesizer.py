from typing import List, Dict, Any
import uuid
from rhesis.synthesizers.base import TestSetSynthesizer
from rhesis.entities.test_set import TestSet


class PromptSynthesizer(TestSetSynthesizer):
    """A synthesizer that generates test cases based on a prompt using LLM."""

    def __init__(self, prompt: str, batch_size: int = 5):
        """
        Initialize the PromptSynthesizer.

        Args:
            prompt: The generation prompt to use
            batch_size: Maximum number of tests to generate in a single LLM call
        """
        super().__init__(batch_size=batch_size)
        self.prompt = prompt

    def _generate_batch(self, num_tests: int) -> List[Dict[str, Any]]:
        """Generate a batch of test cases."""
        formatted_prompt = self.system_prompt.render(
            generation_prompt=self.prompt, num_tests=num_tests
        )

        messages = [
            {"role": "system", "content": formatted_prompt},
            {"role": "user", "content": "Generate the test cases now."},
        ]

        content = self._create_llm_completion(messages)
        test_cases = self._parse_json_response(content)

        # Ensure we get the requested number of test cases
        if len(test_cases) < num_tests:
            for attempt in range(2):  # Try up to 2 more times
                additional_content = self._create_llm_completion(
                    messages,
                    temperature=0.9,  # Increase temperature slightly for variety
                    max_tokens=4000,
                    top_p=0.95,
                )
                additional_cases = self._parse_json_response(additional_content)
                test_cases.extend(additional_cases)

                if len(test_cases) >= num_tests:
                    break

            if len(test_cases) < num_tests:
                raise ValueError(
                    f"LLM returned {len(test_cases)} test cases, expected {num_tests}"
                )

        # Take exactly num_tests results
        test_cases = test_cases[:num_tests]

        return [
            {
                "content": test["prompt"],
                "behavior": test["behavior"],
                "category": test["category"],
                "topic": test["topic"],
                "metadata": {
                    "generated_by": "PromptSynthesizer",
                },
            }
            for test in test_cases
        ]

    def generate(self, **kwargs: Any) -> TestSet:
        """
        Generate test cases based on the given prompt.

        Args:
            **kwargs: Keyword arguments, supports:
                num_tests (int): Total number of test cases to generate. Defaults to 5.

        Returns:
            TestSet: A TestSet entity containing the generated test cases
        """
        num_tests = kwargs.get("num_tests", 5)
        if not isinstance(num_tests, int):
            raise TypeError("num_tests must be an integer")

        all_test_cases = []

        # Generate all tests in a single batch
        all_test_cases = self._generate_batch(num_tests)

        return TestSet(
            id=str(uuid.uuid4()),
            prompts=all_test_cases,
            metadata={
                "generation_prompt": self.prompt,
                "num_tests": num_tests,
                "batch_size": self.batch_size,
                "synthesizer": "PromptSynthesizer",
            },
        )
