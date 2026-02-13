# coding=utf-8
"""
DHC-GEP Package
Dimensional Homogeneity Constrained Gene Expression Programming

This package provides modular and configurable implementation of DHC-GEP algorithm.
"""

__version__ = '1.0.0'
__author__ = 'Wenjun Ma'

from .config import (
    DEFAULT_GEP_CONFIG,
    PARAMETRIC_STUDY_RANGES,
    get_config,
    get_dimension_dict,
    L, M, T, I, Theta, N, J
)

from .core import (
    dimensional_verification,
    gep_simple,
    count_negative_numbers
)

from .utils import (
    protected_division,
    create_fitness_and_individual,
    setup_primitive_set,
    create_toolbox,
    register_genetic_operators,
    create_evaluation_function,
    setup_statistics
)

from .data_utils import (
    load_mat_data,
    prepare_training_data,
    normalize_data,
    denormalize_data,
    DataLoader
)

__all__ = [
    # Config
    'DEFAULT_GEP_CONFIG',
    'PARAMETRIC_STUDY_RANGES',
    'get_config',
    'get_dimension_dict',
    'L', 'M', 'T', 'I', 'Theta', 'N', 'J',
    
    # Core
    'dimensional_verification',
    'gep_simple',
    'count_negative_numbers',
    
    # Utils
    'protected_division',
    'create_fitness_and_individual',
    'setup_primitive_set',
    'create_toolbox',
    'register_genetic_operators',
    'create_evaluation_function',
    'setup_statistics',
    
    # Data Utils
    'load_mat_data',
    'prepare_training_data',
    'normalize_data',
    'denormalize_data',
    'DataLoader'
]
