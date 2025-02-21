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
            return cast(List[Dict[str, str]], parsed)

        raise ValueError(f"Unexpected response format: {content}")

    def _generate_paraphrases(self, prompt: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate paraphrased versions of a single prompt.

        Args:
            prompt: The original prompt to paraphrase

        Returns:
            List[Dict[str, Any]]: List of paraphrased versions, exactly num_paraphrases in length
        """
        formatted_prompt = self.system_prompt.render(
            original_prompt=prompt["content"], num_paraphrases=self.num_paraphrases
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
                "content": p["content"],
                "behavior": prompt["behavior"],
                "category": prompt["category"],
                "topic": prompt["topic"],
                "metadata": {
                    "generated_by": "ParaphrasingSynthesizer",
                    "original_prompt_id": prompt.get("id", "unknown"),
                    "is_paraphrase": True,
                    "original_content": prompt["content"],
                },
            }
            for p in paraphrases
        ]

    def generate(self, **kwargs: Any) -> TestSet:
        """
        Generate paraphrased versions of all prompts in the test set.

        Args:
            **kwargs: Supports:
                num_paraphrases (int): Number of paraphrases to generate per prompt. Defaults to 2.

        Returns:
            TestSet: A TestSet containing original prompts plus their paraphrased versions,
                    with paraphrases appearing immediately after their original prompt
        """
        self.num_paraphrases = kwargs.get("num_paraphrases", 2)
        original_prompts = self.test_set.to_dict()
        all_prompts = []

        def process_prompt(prompt: Dict[str, Any]) -> None:
            """Process a single prompt and its paraphrases."""
            all_prompts.append(prompt)  # Add original
            paraphrases = self._generate_paraphrases(prompt)  # Generate paraphrases
            all_prompts.extend(paraphrases)  # Add paraphrases

        # Use the base class's progress bar
        self._process_with_progress(
            original_prompts,
            process_prompt,
            desc=f"Generating {self.num_paraphrases} paraphrases per prompt",
        )

        return TestSet(
            id=str(uuid.uuid4()),
            prompts=all_prompts,
            metadata={
                "original_test_set_id": self.test_set.fields.get("id", "unknown"),
                "num_paraphrases": self.num_paraphrases,
                "num_original_prompts": len(original_prompts),
                "total_prompts": len(all_prompts),
                "batch_size": self.batch_size,
                "synthesizer": "ParaphrasingSynthesizer",
            },
        )
