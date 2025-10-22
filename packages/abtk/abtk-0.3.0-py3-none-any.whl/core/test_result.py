from dataclasses import dataclass
from typing import Optional
import scipy.stats as sps

@dataclass
class TestResult:
    name_1: str
    value_1: float
    std_1: float
    size_1: int

    name_2: str
    value_2: float
    std_2: float
    size_2: int
    method_name: str
    method_params: dict

    alpha: float
    pvalue: float
    effect: float
    ci_length: float
    left_bound: float
    right_bound: float
    reject: bool

    mde_1: Optional[float] = 0
    mde_2: Optional[float] = 0
    cov_value_1: Optional[float] = 0
    cov_value_2: Optional[float] = 0
    effect_distribution: Optional[sps.norm] = None

    # Multiple comparisons correction metadata
    pvalue_original: Optional[float] = None  # Original p-value before correction
    correction_method: Optional[str] = None  # Name of correction method used
