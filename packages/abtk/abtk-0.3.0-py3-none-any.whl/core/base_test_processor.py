"""
Base class for all statistical test processors.

This module provides the abstract base class that all test processors should inherit from.
It defines the common interface and shared functionality for statistical tests.
"""

from abc import ABC, abstractmethod
from typing import List
import logging

from core.data_types import SampleData
from core.test_result import TestResult


class BaseTestProcessor(ABC):
    """
    Abstract base class for all statistical test processors.

    All test processors should inherit from this class and implement
    the required abstract methods.

    Parameters
    ----------
    test_name : str
        Name of the statistical test
    alpha : float
        Significance level for hypothesis testing
    logger : logging.Logger, optional
        Logger instance for error reporting
    **test_params : dict
        Additional test-specific parameters
    """

    def __init__(
        self,
        test_name: str,
        alpha: float = 0.05,
        logger: logging.Logger = None,
        **test_params
    ):
        self.test_name = test_name
        self.alpha = alpha
        self.logger = logger or logging.getLogger(__name__)
        self.test_params = test_params

    @abstractmethod
    def compare(self, samples: List[SampleData]) -> List[TestResult]:
        """
        Compare samples and return test results.

        This is the main entry point for running the statistical test.
        It performs all pairwise comparisons if multiple samples are provided.

        Parameters
        ----------
        samples : List[SampleData]
            List of samples to compare

        Returns
        -------
        List[TestResult]
            List of test results for all pairwise comparisons

        Examples
        --------
        >>> test = TTest(alpha=0.05)
        >>> results = test.compare([control, treatment])
        >>> print(results[0].effect)
        """
        pass

    @abstractmethod
    def compare_samples(self, sample1: SampleData, sample2: SampleData) -> TestResult:
        """
        Compare two samples using the statistical test.

        Parameters
        ----------
        sample1 : SampleData
            First sample (control/baseline)
        sample2 : SampleData
            Second sample (treatment/variant)

        Returns
        -------
        TestResult
            Test result with p-value, effect size, confidence interval, etc.
        """
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(test_name='{self.test_name}', alpha={self.alpha})"
