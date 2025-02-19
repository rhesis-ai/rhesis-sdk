from abc import ABC, abstractmethod
from typing import Any
from rhesis.entities.test_set import TestSet


class TestSetSynthesizer(ABC):
    """Base class for all test set synthesizers."""

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
