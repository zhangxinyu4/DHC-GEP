# coding=utf-8
"""
Configuration module for DHC-GEP parameters.
This module centralizes all configurable parameters to avoid hardcoding values across multiple scripts.
"""

from fractions import Fraction

# Base dimensional prime numbers
# Used for dimensional verification in physical equations
L, M, T, I, Theta, N, J = 2, 3, 5, 7, 11, 13, 17

# Default GEP Algorithm Parameters
DEFAULT_GEP_CONFIG = {
    # Gene structure
    'head_length': 15,              # Length of gene head
    'n_genes': 2,                   # Number of genes in a chromosome
    'rnc_array_length': 15,         # Length of random numerical constant (RNC) array
    
    # RNC generation
    'rnc_min': -10,                 # Minimum value for RNC
    'rnc_max': 10,                  # Maximum value for RNC
    
    # Population parameters
    'n_population': 1660,           # Number of individuals in population
    'n_generations': 200,           # Maximum number of generations
    'n_elites': 1,                  # Number of elite individuals preserved
    'n_champions': 3,               # Number of best individuals to track
    
    # Selection
    'tournament_size': 3,           # Tournament selection size
    
    # Mutation probabilities
    'mut_uniform_pb': 1,            # Uniform mutation probability
    'mut_uniform_ind_pb': 0.05,     # Individual probability for uniform mutation
    'mut_invert_pb': 0.1,           # Inversion mutation probability
    'mut_is_transpose_pb': 0.1,     # IS transposition probability
    'mut_ris_transpose_pb': 0.1,    # RIS transposition probability
    'mut_gene_transpose_pb': 0.1,   # Gene transposition probability
    
    # Crossover probabilities
    'cx_1p_pb': 0.3,                # One-point crossover probability
    'cx_2p_pb': 0.2,                # Two-point crossover probability
    'cx_gene_pb': 0.1,              # Gene crossover probability
    
    # Dc-specific operators (for GeneDc)
    'mut_dc_pb': 1,                 # Dc domain uniform mutation probability
    'mut_dc_ind_pb': 0.05,          # Individual probability for Dc mutation
    'mut_invert_dc_pb': 0.1,        # Dc inversion probability
    'mut_transpose_dc_pb': 0.1,     # Dc transposition probability
    'mut_rnc_array_dc_pb': 1,       # RNC array mutation probability
    'mut_rnc_array_dc_ind_pb': '0.5p',  # Individual probability for RNC array mutation
    
    # Convergence and termination
    'tolerance': 1e-3,              # Error tolerance for early termination
    'check_interval': 20,           # Generations between output checks
    'termination_check_interval': 100,  # Generations between termination checks
    
    # Output and logging
    'output_dir': 'output',         # Directory for output files
    'pkl_dir': 'pkl',               # Directory for saved populations
    'verbose': True,                # Print evolution statistics
    
    # Linear scaling
    'enable_linear_scaling': True,  # Whether to apply linear scaling
    
    # Evaluation
    'protected_div_threshold': 1e-10,   # Threshold for protected division
    'invalid_fitness': 1000,            # Fitness assigned to invalid individuals
    'invalid_marker': 1e18,             # Marker for invalid individuals
}

# Parametric study ranges
PARAMETRIC_STUDY_RANGES = {
    'head_length': [3, 5, 7, 9, 11, 13, 15],
    'n_genes': [1, 2],
    'n_population': [200, 400, 600, 800, 1000],
}


def get_config(**overrides):
    """
    Get a configuration dictionary with optional overrides.
    
    Args:
        **overrides: Keyword arguments to override default config values
        
    Returns:
        dict: Configuration dictionary with overrides applied
        
    Example:
        config = get_config(head_length=10, n_population=500)
    """
    config = DEFAULT_GEP_CONFIG.copy()
    config.update(overrides)
    return config


def create_dimension_dict(**dimensions):
    """
    Create a dimension dictionary with Fraction values.
    
    Args:
        **dimensions: Keyword arguments where keys are variable names and
                     values are dimension expressions
                     
    Returns:
        dict: Dictionary mapping variable names to Fraction dimensions
        
    Example:
        dims = create_dimension_dict(
            rho=Fraction(M, L**3),
            velocity=Fraction(L, T)
        )
    """
    return {k: v if isinstance(v, Fraction) else Fraction(v) for k, v in dimensions.items()}


# Common dimension definitions for typical problems
COMMON_DIMENSIONS = {
    # Diffusion equation variables
    'diffusion': {
        'rho': Fraction(M, L**3),
        'rho_y': Fraction(M, L**4),
        'rho_yy': Fraction(M, L**5),
        'rho_3y': Fraction(M, L**6),
        'df_c': Fraction(L**2, T),
        'Miu': Fraction(M, L*T),
        'target': Fraction(M, T*L**3),
    },
    
    # Flow equation variables
    'flow': {
        'velocity': Fraction(L, T),
        'pressure': Fraction(M, L*T**2),
        'density': Fraction(M, L**3),
        'viscosity': Fraction(M, L*T),
    }
}


def get_dimension_dict(problem_type=None, **custom_dims):
    """
    Get a dimension dictionary for a specific problem type or custom dimensions.
    
    Args:
        problem_type (str, optional): Type of problem ('diffusion', 'flow', etc.)
        **custom_dims: Custom dimension specifications to add or override
        
    Returns:
        dict: Dimension dictionary for the specified problem
        
    Example:
        dims = get_dimension_dict('diffusion')
        dims = get_dimension_dict(custom_var=Fraction(M, L**2))
    """
    if problem_type and problem_type in COMMON_DIMENSIONS:
        dims = COMMON_DIMENSIONS[problem_type].copy()
        dims.update(custom_dims)
        return dims
    return create_dimension_dict(**custom_dims)
