"""
DHC-GEP: Dimensional Homogeneity Constrained Gene Expression Programming

A centralized package for DHC-GEP algorithms with optimized dimensional verification.
"""

from .core import dimensional_verification, gep_simple
from .config import get_dimension_config, SEVEN_BASE_DIMENSIONS

__version__ = '1.0.0'
__all__ = [
    'dimensional_verification',
    'gep_simple',
    'get_dimension_config',
    'SEVEN_BASE_DIMENSIONS'
]
