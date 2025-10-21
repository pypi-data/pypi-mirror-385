# Contributing to ABTK

Thank you for your interest in contributing to ABTK! This guide will help you get started.

## Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/abtk.git
cd abtk
```

### 2. Install Development Dependencies

```bash
# Install with development tools
pip install -e ".[dev]"

# This installs:
# - pytest (testing)
# - pytest-cov (coverage)
# - black (code formatting)
# - flake8 (linting)
# - mypy (type checking)
```

### 3. Run Tests

```bash
# Run all tests
pytest unit_tests/

# Run with coverage
pytest --cov=. unit_tests/

# Run specific test file
pytest unit_tests/test_ancova.py

# Run with verbose output
pytest -v unit_tests/
```

## Project Structure

```
abtk/
├── core/                    # Core data structures
│   ├── base_test_processor.py
│   ├── data_types.py
│   ├── test_result.py
│   └── quantile_test_result.py
│
├── tests/                   # Statistical tests (domain logic)
│   ├── parametric/          # TTest, ZTest, CUPED, ANCOVA, etc.
│   └── nonparametric/       # Bootstrap tests
│
├── utils/                   # Shared utilities
│   ├── bootstrap/           # Bootstrap utilities
│   ├── corrections.py       # Multiple comparisons
│   ├── quantile_analysis.py # Quantile treatment effects
│   └── visualization.py     # Plotting (optional)
│
├── unit_tests/              # Unit tests (pytest)
│   └── test_*.py
│
├── examples/                # Executable examples
│   └── *.py
│
└── docs/                    # Documentation
    ├── getting-started.md
    ├── user-guide/
    ├── api-reference/
    └── examples/
```

## Adding a New Statistical Test

### Step 1: Create Test Class

Create a new file in `tests/parametric/` or `tests/nonparametric/`:

```python
# tests/parametric/my_new_test.py

from typing import List, Literal, Optional
import logging
from itertools import combinations
import numpy as np

from core.base_test_processor import BaseTestProcessor
from core.data_types import SampleData
from core.test_result import TestResult
from utils.data_validation import validate_samples, validate_alpha

class MyNewTest(BaseTestProcessor):
    """
    Brief description of your test.

    Longer description explaining when to use this test,
    what it does, and how it differs from other tests.

    Parameters
    ----------
    alpha : float, default=0.05
        Significance level
    test_type : {'relative', 'absolute'}, default='relative'
        Type of effect to calculate
    logger : logging.Logger, optional
        Logger instance

    Examples
    --------
    >>> from core.data_types import SampleData
    >>> from tests.parametric import MyNewTest
    >>>
    >>> control = SampleData(data=[100, 110, 95], name="Control")
    >>> treatment = SampleData(data=[105, 115, 100], name="Treatment")
    >>>
    >>> test = MyNewTest(alpha=0.05)
    >>> results = test.compare([control, treatment])
    >>>
    >>> result = results[0]
    >>> print(f"Effect: {result.effect:.2%}")

    Notes
    -----
    - Explain assumptions
    - When to use vs not use
    - Comparison to similar tests
    """

    def __init__(
        self,
        alpha: float = 0.05,
        test_type: Literal["relative", "absolute"] = "relative",
        logger: Optional[logging.Logger] = None,
    ):
        # Validate parameters
        validate_alpha(alpha)

        if test_type not in ["relative", "absolute"]:
            raise ValueError('Invalid test_type. Use "relative" or "absolute"')

        # Initialize base class
        super().__init__(
            test_name="my-new-test",
            alpha=alpha,
            logger=logger,
            test_type=test_type
        )

        self.test_type = test_type

    def compare(self, samples: List[SampleData]) -> List[TestResult]:
        """
        Compare multiple samples and perform pairwise tests.

        Parameters
        ----------
        samples : List[SampleData]
            List of samples to compare

        Returns
        -------
        List[TestResult]
            List of pairwise comparison results
        """
        if not samples or len(samples) < 2:
            return []

        validate_samples(samples, min_samples=2)

        results = []
        for sample1, sample2 in combinations(samples, 2):
            results.append(self.compare_samples(sample1, sample2))

        return results

    def compare_samples(
        self,
        sample1: SampleData,
        sample2: SampleData
    ) -> TestResult:
        """
        Compare two samples using your statistical test.

        Parameters
        ----------
        sample1 : SampleData
            First sample
        sample2 : SampleData
            Second sample

        Returns
        -------
        TestResult
            Test result with p-value, effect, CI, etc.
        """
        try:
            # 1. Calculate your test statistic
            stat1 = np.mean(sample1.data)
            stat2 = np.mean(sample2.data)

            # 2. Calculate effect
            if self.test_type == "absolute":
                effect = stat2 - stat1
            else:  # relative
                effect = stat2 / stat1 - 1

            # 3. Calculate p-value (your test logic here)
            pvalue = 0.05  # Replace with actual calculation

            # 4. Calculate confidence interval
            left_bound = effect - 0.05  # Replace with actual calculation
            right_bound = effect + 0.05  # Replace with actual calculation
            ci_length = right_bound - left_bound

            # 5. Make decision
            reject = pvalue < self.alpha

            # 6. Create result
            result = TestResult(
                name_1=sample1.name or "sample_1",
                value_1=stat1,
                std_1=np.std(sample1.data),
                size_1=sample1.sample_size,
                name_2=sample2.name or "sample_2",
                value_2=stat2,
                std_2=np.std(sample2.data),
                size_2=sample2.sample_size,
                method_name=self.test_name,
                method_params=self.test_params,
                alpha=self.alpha,
                pvalue=pvalue,
                effect=effect,
                ci_length=ci_length,
                left_bound=left_bound,
                right_bound=right_bound,
                reject=reject
            )

            return result

        except Exception as e:
            self.logger.error(f"Error in MyNewTest: {str(e)}", exc_info=True)
            raise
```

### Step 2: Add to __init__.py

Add your test to the appropriate `__init__.py`:

```python
# tests/parametric/__init__.py

from .my_new_test import MyNewTest

__all__ = [
    'TTest',
    'PairedTTest',
    # ... existing tests ...
    'MyNewTest',  # Add your test
]
```

### Step 3: Write Unit Tests

Create test file in `unit_tests/`:

```python
# unit_tests/test_my_new_test.py

import pytest
import numpy as np
from core.data_types import SampleData
from tests.parametric import MyNewTest

class TestMyNewTestInitialization:
    """Test initialization and parameters."""

    def test_default_initialization(self):
        test = MyNewTest()
        assert test.alpha == 0.05
        assert test.test_type == "relative"

    def test_custom_parameters(self):
        test = MyNewTest(alpha=0.01, test_type="absolute")
        assert test.alpha == 0.01
        assert test.test_type == "absolute"

    def test_invalid_alpha(self):
        with pytest.raises(ValueError):
            MyNewTest(alpha=-0.05)

class TestMyNewTestComparison:
    """Test actual comparisons."""

    def test_simple_comparison(self):
        np.random.seed(42)

        control = SampleData(
            data=np.random.normal(100, 10, 50),
            name="Control"
        )
        treatment = SampleData(
            data=np.random.normal(110, 10, 50),
            name="Treatment"
        )

        test = MyNewTest(alpha=0.05)
        results = test.compare([control, treatment])

        assert len(results) == 1
        result = results[0]

        # Check result properties
        assert result.effect > 0  # Treatment should be higher
        assert 0 <= result.pvalue <= 1
        assert result.left_bound < result.right_bound

    def test_relative_vs_absolute(self):
        control = SampleData(data=[100, 110, 90], name="Control")
        treatment = SampleData(data=[110, 121, 99], name="Treatment")

        # Relative
        test_rel = MyNewTest(test_type="relative")
        result_rel = test_rel.compare([control, treatment])[0]

        # Absolute
        test_abs = MyNewTest(test_type="absolute")
        result_abs = test_abs.compare([control, treatment])[0]

        # Relationship: absolute = relative * control_mean
        assert result_abs.effect == pytest.approx(
            result_rel.effect * np.mean(control.data),
            rel=0.01
        )
```

### Step 4: Add Documentation

Create user guide in `docs/user-guide/`:

```markdown
# My New Test Guide

## Overview

Description of your test...

## When to Use

- Use case 1
- Use case 2

## Example

\`\`\`python
from tests.parametric import MyNewTest

test = MyNewTest(alpha=0.05)
results = test.compare([control, treatment])
\`\`\`

## Parameters

...
```

### Step 5: Add Example

Create runnable example in `examples/`:

```python
# examples/my_new_test_example.py

"""
Example usage of MyNewTest.
"""

import numpy as np
from core.data_types import SampleData
from tests.parametric import MyNewTest

# Generate sample data
np.random.seed(42)

control = SampleData(
    data=np.random.normal(100, 15, 1000),
    name="Control"
)

treatment = SampleData(
    data=np.random.normal(105, 15, 1000),
    name="Treatment"
)

# Run test
test = MyNewTest(alpha=0.05, test_type="relative")
results = test.compare([control, treatment])

# Display results
result = results[0]
print(f"\\nTest: {result.method_name}")
print(f"Effect: {result.effect:.2%}")
print(f"P-value: {result.pvalue:.4f}")
print(f"Significant: {result.reject}")
print(f"95% CI: [{result.left_bound:.2%}, {result.right_bound:.2%}]")
```

## Code Style

### Formatting

We use `black` for code formatting:

```bash
# Format all Python files
black .

# Check formatting without changing files
black --check .
```

### Linting

We use `flake8` for linting:

```bash
flake8 . --max-line-length=100
```

### Type Hints

Use type hints for function signatures:

```python
def compare_samples(
    self,
    sample1: SampleData,
    sample2: SampleData
) -> TestResult:
    pass
```

### Docstrings

Use NumPy-style docstrings:

```python
def my_function(param1: int, param2: str) -> bool:
    """
    Brief description.

    Longer description if needed.

    Parameters
    ----------
    param1 : int
        Description of param1
    param2 : str
        Description of param2

    Returns
    -------
    bool
        Description of return value

    Examples
    --------
    >>> my_function(5, "test")
    True
    """
    pass
```

## Testing Guidelines

### Test Structure

Organize tests into classes:

```python
class TestMyFeatureInitialization:
    """Test initialization and parameters."""
    pass

class TestMyFeatureValidation:
    """Test input validation."""
    pass

class TestMyFeatureComparison:
    """Test actual comparisons."""
    pass
```

### Test Naming

- Test files: `test_*.py`
- Test classes: `Test*`
- Test functions: `test_*`

### Assertions

Use pytest's assert with informative messages:

```python
assert result.effect > 0, f"Expected positive effect, got {result.effect}"
assert result.pvalue == pytest.approx(0.05, abs=0.01)
```

### Fixtures

Use pytest fixtures for common setup:

```python
@pytest.fixture
def sample_data():
    return SampleData(
        data=np.random.normal(100, 10, 50),
        name="Test"
    )

def test_something(sample_data):
    assert sample_data.sample_size == 50
```

## Documentation Guidelines

### User Guides

- Write for analysts, not developers
- Include real-world examples
- Explain **when** to use, not just **how**
- Compare to similar methods

### API Reference

- Complete parameter descriptions
- Include return value descriptions
- Add examples
- Document exceptions

### Examples

- Self-contained (can be run independently)
- Use realistic data
- Show common patterns
- Include output

## Pull Request Process

1. **Create a branch**
   ```bash
   git checkout -b feature/my-new-test
   ```

2. **Make changes**
   - Write code
   - Add tests
   - Update documentation

3. **Run tests**
   ```bash
   pytest unit_tests/
   black .
   flake8 .
   ```

4. **Commit**
   ```bash
   git add .
   git commit -m "Add MyNewTest for ..."
   ```

5. **Push and create PR**
   ```bash
   git push origin feature/my-new-test
   ```

## Questions?

- Check [FAQ](docs/faq.md)
- Ask on [GitHub Issues](https://github.com/yourusername/abtk/issues)
- Review existing tests for patterns

## Code of Conduct

- Be respectful
- Provide constructive feedback
- Help others learn
- Focus on code quality

Thank you for contributing to ABTK!
