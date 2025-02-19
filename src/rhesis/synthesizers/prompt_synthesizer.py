from typing import List, Dict, Any, Optional
import json
from pathlib import Path
from tqdm.auto import tqdm
from jinja2 import Template
from rhesis.synthesizers.base import TestSetSynthesizer
from rhesis.entities.test_set import TestSet
from rhesis.services import LLMService
import uuid

class PromptSynthesizer(TestSetSynthesizer):
    """A synthesizer that generates test cases based on a prompt using LLM."""
    
    def __init__(self, prompt: str, batch_size: int = 5):
        """
        Initialize the PromptSynthesizer.
        
        Args:
            prompt: The generation prompt to use
            batch_size: Maximum number of tests to generate in a single LLM call
        """
        self.prompt = prompt
        self.batch_size = batch_size
        self.llm_service = LLMService()
        prompt_path = Path(__file__).parent / 'assets' / 'prompt_synthesizer.md'
        with open(prompt_path, 'r') as f:
            template = Template(f.read())
            self.system_prompt = template
    
    def _parse_test_cases(self, content: str) -> List[Dict[str, str]]:
        """Parse the LLM response content into a list of test cases."""
        parsed = json.loads(content)
        
        # Handle response wrapped in test_cases
        if isinstance(parsed, dict) and 'test_cases' in parsed:
            return parsed['test_cases']
        
        # Handle direct list response
        if isinstance(parsed, list):
            return parsed
            
        # Handle single test case
        if isinstance(parsed, dict):
            return [parsed]
            
        raise ValueError(f"Unexpected response format: {content}")
    
    def _generate_batch(self, num_tests: int) -> List[Dict[str, Any]]:
        """Generate a batch of test cases."""
        formatted_prompt = self.system_prompt.render(
            generation_prompt=self.prompt,
            num_tests=num_tests
        )
        
        messages = [
            {"role": "system", "content": formatted_prompt},
            {"role": "user", "content": "Generate the test cases now."}
        ]
        
        response = self.llm_service.create_completion(
            messages=messages,
            temperature=0.8,
            max_tokens=4000,
            top_p=0.95
        )
        
        content = response['choices'][0]['message']['content']
        return self._parse_test_cases(content)
    
    def generate(self, num_tests: Optional[int] = 5) -> TestSet:
        """
        Generate test cases based on the given prompt.
        
        Args:
            num_tests: Total number of test cases to generate
            
        Returns:
            TestSet: A TestSet entity containing the generated test cases
        """
        all_test_cases = []
        remaining_tests = num_tests
        
        pbar = tqdm(total=num_tests, desc="Generating test cases")
        while remaining_tests > 0:
            batch_size = min(remaining_tests, self.batch_size)
            batch_cases = self._generate_batch(batch_size)
            new_tests = len(batch_cases)
            all_test_cases.extend(batch_cases)
            pbar.update(new_tests)
            remaining_tests = num_tests - len(all_test_cases)
            
            if len(all_test_cases) >= num_tests:
                break
        
        pbar.close()
        
        # Ensure we don't return more tests than requested
        all_test_cases = all_test_cases[:num_tests]
        
        prompts = [
            {
                "content": test["prompt"],
                "behavior": test["behavior"],
                "category": test["category"],
                "topic": test["topic"],
                "metadata": {
                    "generated_by": "PromptSynthesizer",
                }
            }
            for test in all_test_cases
        ]
        
        return TestSet(
            id=str(uuid.uuid4()),
            prompts=prompts,
            metadata={
                "generation_prompt": self.prompt,
                "num_tests": num_tests,
                "batch_size": self.batch_size,
                "synthesizer": "PromptSynthesizer"
            }
        ) 