# coding=utf-8
"""
Utility functions for DHC-GEP experiments.

This module provides common utilities for setting up GEP experiments,
including toolbox creation, operator registration, and evaluation functions.
"""

import operator
import random
import numpy as np
import geppy as gep
from deap import creator, base, tools
from .config import DEFAULT_GEP_CONFIG


def protected_division(x1, x2, threshold=1e-10):
    """
    Protected division to avoid division by zero.
    
    Args:
        x1: Numerator
        x2: Denominator
        threshold: Minimum absolute value for denominator (default: 1e-10)
        
    Returns:
        float: Result of division or 1 if denominator is too small
    """
    if abs(x2) < threshold:
        return 1
    return x1 / x2


def create_fitness_and_individual():
    """
    Create fitness and individual classes for minimization problems.
    
    Returns:
        tuple: (FitnessMin class, Individual class)
    """
    if not hasattr(creator, "FitnessMin"):
        creator.create("FitnessMin", base.Fitness, weights=(-1,))
    if not hasattr(creator, "Individual"):
        creator.create("Individual", gep.Chromosome, fitness=creator.FitnessMin)
    
    return creator.FitnessMin, creator.Individual


def setup_primitive_set(input_names, constants=None, operators='basic'):
    """
    Set up a primitive set with common operators and terminals.
    
    Args:
        input_names: List of input variable names
        constants: Dictionary of constant names and values (optional)
        operators: Type of operators to include ('basic', 'extended', 'minimal')
                  - 'basic': add, sub, mul, truediv
                  - 'extended': basic + pow, sqrt, etc.
                  - 'minimal': add, mul only
                  
    Returns:
        PrimitiveSet: Configured primitive set
    """
    pset = gep.PrimitiveSet('Main', input_names=input_names)
    
    # Add constants if provided
    if constants:
        for name, value in constants.items():
            pset.add_symbol_terminal(name, value)
    
    # Add operators based on type
    if operators in ['basic', 'extended']:
        pset.add_function(operator.add, 2)
        pset.add_function(operator.sub, 2)
        pset.add_function(operator.mul, 2)
        pset.add_function(operator.truediv, 2)
    elif operators == 'minimal':
        pset.add_function(operator.add, 2)
        pset.add_function(operator.mul, 2)
    
    # Add RNC terminal
    pset.add_rnc_terminal()
    
    # Set numpy to raise on division errors
    np.seterr(divide='raise')
    
    return pset


def create_toolbox(pset, config=None):
    """
    Create and configure a GEP toolbox with standard operators.
    
    Args:
        pset: Primitive set
        config: Configuration dictionary (uses DEFAULT_GEP_CONFIG if None)
        
    Returns:
        gep.Toolbox: Configured toolbox
    """
    if config is None:
        config = DEFAULT_GEP_CONFIG
    
    # Create fitness and individual classes
    create_fitness_and_individual()
    
    toolbox = gep.Toolbox()
    
    # Register RNC generator
    toolbox.register('rnc_gen', random.randint, 
                    a=config['rnc_min'], 
                    b=config['rnc_max'])
    
    # Register gene generator
    toolbox.register('gene_gen', gep.GeneDc, 
                    pset=pset, 
                    head_length=config['head_length'],
                    rnc_gen=toolbox.rnc_gen, 
                    rnc_array_length=config['rnc_array_length'])
    
    # Register individual and population
    toolbox.register('individual', creator.Individual, 
                    gene_gen=toolbox.gene_gen, 
                    n_genes=config['n_genes'], 
                    linker=operator.add)
    
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    
    # Register compilation
    toolbox.register('compile', gep.compile_, pset=pset)
    
    return toolbox


def register_genetic_operators(toolbox, config=None):
    """
    Register genetic operators in the toolbox.
    
    Args:
        toolbox: GEP toolbox
        config: Configuration dictionary (uses DEFAULT_GEP_CONFIG if None)
    """
    if config is None:
        config = DEFAULT_GEP_CONFIG
    
    # Selection operator
    toolbox.register('select', tools.selTournament, 
                    tournsize=config['tournament_size'])
    
    # General mutation operators
    toolbox.register('mut_uniform', gep.mutate_uniform, 
                    pset=toolbox.gene_gen.keywords['pset'],
                    ind_pb=config['mut_uniform_ind_pb'], 
                    pb=config['mut_uniform_pb'])
    
    toolbox.register('mut_invert', gep.invert, 
                    pb=config['mut_invert_pb'])
    
    toolbox.register('mut_is_transpose', gep.is_transpose, 
                    pb=config['mut_is_transpose_pb'])
    
    toolbox.register('mut_ris_transpose', gep.ris_transpose, 
                    pb=config['mut_ris_transpose_pb'])
    
    toolbox.register('mut_gene_transpose', gep.gene_transpose, 
                    pb=config['mut_gene_transpose_pb'])
    
    # Crossover operators
    toolbox.register('cx_1p', gep.crossover_one_point, 
                    pb=config['cx_1p_pb'])
    
    toolbox.register('cx_2p', gep.crossover_two_point, 
                    pb=config['cx_2p_pb'])
    
    toolbox.register('cx_gene', gep.crossover_gene, 
                    pb=config['cx_gene_pb'])
    
    # Dc-specific operators
    toolbox.register('mut_dc', gep.mutate_uniform_dc, 
                    ind_pb=config['mut_dc_ind_pb'], 
                    pb=config['mut_dc_pb'])
    
    toolbox.register('mut_invert_dc', gep.invert_dc, 
                    pb=config['mut_invert_dc_pb'])
    
    toolbox.register('mut_transpose_dc', gep.transpose_dc, 
                    pb=config['mut_transpose_dc_pb'])
    
    toolbox.register('mut_rnc_array_dc', gep.mutate_rnc_array_dc, 
                    rnc_gen=toolbox.rnc_gen,
                    ind_pb=config['mut_rnc_array_dc_ind_pb'])
    
    toolbox.pbs['mut_rnc_array_dc'] = config['mut_rnc_array_dc_pb']


def create_evaluation_function(X_data, y_data, dim_verification_func=None,
                               dict_of_dimension=None, target_dimension=None,
                               linear_scaling=True, invalid_fitness=1000,
                               invalid_marker=1e18):
    """
    Create an evaluation function for GEP individuals.
    
    Args:
        X_data: Input data (tuple/list of arrays for each variable)
        y_data: Target output data
        dim_verification_func: Dimensional verification function (optional)
        dict_of_dimension: Dimension dictionary for verification (optional)
        target_dimension: Target dimension for verification (optional)
        linear_scaling: Whether to apply linear scaling (default: True)
        invalid_fitness: Fitness value for invalid individuals (default: 1000)
        invalid_marker: Marker value for invalid individuals (default: 1e18)
        
    Returns:
        function: Evaluation function for use with toolbox
    """
    
    def evaluate_with_linear_scaling(individual, toolbox):
        """Evaluate with dimensional verification and linear scaling."""
        # Check dimensional homogeneity
        if dim_verification_func is not None:
            validity = dim_verification_func(individual, dict_of_dimension, target_dimension)
            if not validity:
                individual.a = invalid_marker
                return invalid_fitness,
        
        # Compile and evaluate
        func = toolbox.compile(individual)
        try:
            Yp = np.array(list(map(func, *X_data)))
        except (FloatingPointError, ZeroDivisionError):
            individual.a = invalid_marker
            return invalid_fitness,
        
        if isinstance(Yp, np.ndarray):
            Q = np.reshape(Yp, (-1, 1)).astype('float32')
            Q = np.nan_to_num(Q)
            
            # Apply linear scaling
            individual.a, residuals, _, _ = np.linalg.lstsq(Q, y_data, rcond=None)
            
            # Calculate mean relative error
            c = individual.a.reshape(-1, 1)
            relative_error = (np.dot(Q, c) - y_data) / y_data
            
            if residuals.size > 0:
                return np.mean(np.abs(relative_error)),
        
        # Fallback
        individual.a = 0
        relative_error = (y_data - individual.a) / y_data
        return np.mean(np.abs(relative_error)),
    
    def evaluate_simple(individual, toolbox):
        """Simple evaluation without dimensional verification."""
        func = toolbox.compile(individual)
        Yp = np.array(list(map(func, *X_data)))
        return np.mean(np.abs((y_data - Yp) / y_data)),
    
    if linear_scaling and dim_verification_func is not None:
        return evaluate_with_linear_scaling
    else:
        return evaluate_simple


def setup_statistics():
    """
    Create standard statistics object for tracking evolution.
    
    Returns:
        deap.tools.Statistics: Configured statistics object
    """
    stats = tools.Statistics(key=lambda ind: ind.fitness.values[0])
    stats.register("avg", np.mean)
    stats.register("std", np.std)
    stats.register("min", np.min)
    stats.register("max", np.max)
    return stats


__all__ = [
    'protected_division',
    'create_fitness_and_individual',
    'setup_primitive_set',
    'create_toolbox',
    'register_genetic_operators',
    'create_evaluation_function',
    'setup_statistics'
]
