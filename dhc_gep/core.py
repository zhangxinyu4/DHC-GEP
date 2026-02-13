# coding=utf-8

"""
Core DHC-GEP module providing dimensional verification and enhanced GEP algorithms.

This module consolidates the DHC-GEP functionality that was previously duplicated
across multiple directories. It provides:
- Dimensional verification for physical equations
- Enhanced GEP evolution with real-time output and termination criteria
- Population saving and restarting capabilities

Original author: Wenjun Ma
Modified for modular architecture and maintainability
"""

from fractions import Fraction
import os
import deap
import random
import warnings
import numpy as np
import pickle
import datetime
import geppy as gep
import time


def dimensional_verification(individual, dict_of_dimension, target_dimension, use_protected_div=False):
    """
    Verify whether an individual satisfies dimensional homogeneity.
    
    This function checks if the dimensions of an expression tree satisfy
    dimensional homogeneity by propagating dimensions from leaves to root
    and comparing with the target dimension.
    
    Args:
        individual: GEP individual to verify
        dict_of_dimension: Dictionary mapping terminal names to their Fraction dimensions
        target_dimension: Target dimension as a Fraction
        use_protected_div: If True, use 'protected_div' operator name instead of 'truediv'
        
    Returns:
        bool: True if the individual is dimensionally homogeneous, False otherwise
    """

    def my_add(a, b):
        if isinstance(a, bool) or isinstance(b, bool):
            return False
        if isinstance(a, int):
            a = Fraction(1)
        if isinstance(b, int):
            b = Fraction(1)

        if a == b:
            return a
        else:
            return False

    def my_sub(a, b):
        if isinstance(a, bool) or isinstance(b, bool):
            return False
        if isinstance(a, int):
            a = Fraction(1)
        if isinstance(b, int):
            b = Fraction(1)

        if a == b:
            return a
        else:
            return False

    def my_mul(a, b):
        if isinstance(a, bool) or isinstance(b, bool):
            return False
        if isinstance(a, int):
            a = Fraction(1)
        if isinstance(b, int):
            b = Fraction(1)

        return a * b

    def my_div(a, b):
        if isinstance(a, bool) or isinstance(b, bool) or b == 0:
            return False
        if isinstance(a, int):
            a = Fraction(1)
        if isinstance(b, int):
            b = Fraction(1)

        return a / b
    
    # Convert individual to string and replace operators with dimensional check functions
    individual_expr = individual.__str__().replace('\t', '').replace('\n', '')
    individual_expr = individual_expr.replace('add', 'my_add')
    individual_expr = individual_expr.replace('sub', 'my_sub')
    individual_expr = individual_expr.replace('mul', 'my_mul')
    
    # Handle both 'truediv' and 'protected_div' operator names
    if use_protected_div:
        individual_expr = individual_expr.replace('protected_div', 'my_div')
    else:
        individual_expr = individual_expr.replace('truediv', 'my_div')
    
    # Create local variables for evaluation
    create_var = locals()
    create_var.update(dict_of_dimension)
    
    # Evaluate dimensional expression
    dimension_of_DDEq = eval(individual_expr)
    
    return dimension_of_DDEq == target_dimension


def count_negative_numbers(arr):
    """
    Count the number of negative values in an array.
    
    Args:
        arr: NumPy array or list
        
    Returns:
        int: Count of negative numbers
    """
    return np.sum(arr < 0) if isinstance(arr, np.ndarray) else sum(1 for num in arr if num < 0)


def _validate_basic_toolbox(tb):
    """
    Validate the operators in the toolbox according to GEP conventions.
    
    Args:
        tb: deap.base.Toolbox object
    """
    assert hasattr(tb, 'select'), "The toolbox must have a 'select' operator."
    
    # Check if all operators in .pbs are registered
    for op in tb.pbs:
        assert op.startswith('mut') or op.startswith('cx'), \
            "Operators must start with 'mut' or 'cx' except selection."
        assert hasattr(tb, op), \
            f"Probability for operator '{op}' is specified, but not registered in toolbox."
    
    # Check if all mut_/cx_ operators have probabilities assigned
    for op in [attr for attr in dir(tb) if attr.startswith('mut') or attr.startswith('cx')]:
        if op not in tb.pbs:
            warnings.warn(
                f'{op} is registered, but its probability is NOT assigned in Toolbox.pbs. '
                f'By default, the probability is ZERO and {op} will NOT be applied.',
                category=UserWarning
            )


def _apply_modification(population, operator, pb):
    """
    Apply modification operator to each individual in population with probability pb.
    
    Args:
        population: List of individuals
        operator: Modification operator function
        pb: Probability of applying the operator
        
    Returns:
        list: Modified population
    """
    for i in range(len(population)):
        if random.random() < pb:
            population[i], = operator(population[i])
            del population[i].fitness.values
    return population


def _apply_crossover(population, operator, pb):
    """
    Mate the population in place using crossover operator with probability pb.
    
    Args:
        population: List of individuals
        operator: Crossover operator function
        pb: Probability of applying the operator
        
    Returns:
        list: Population after crossover
    """
    for i in range(1, len(population), 2):
        if random.random() < pb:
            population[i - 1], population[i] = operator(population[i - 1], population[i])
            del population[i - 1].fitness.values
            del population[i].fitness.values
    return population


def gep_simple(population, toolbox, n_generations=100, n_elites=1,
               stats=None, hall_of_fame=None, verbose=__debug__, 
               tolerance=1e-10, GEP_type='', check_interval=20,
               termination_check_interval=100, output_dir='output', pkl_dir='pkl',
               evaluate_no_loss_entropy=None):
    """
    Enhanced GEP algorithm with dimensional verification and real-time monitoring.
    
    This is a modified version of the standard GEP algorithm that adds:
    - Real-time output of best individuals to .dat files
    - Population saving to .pkl files for restarting
    - Early termination based on error tolerance
    - Optional entropy loss evaluation
    
    Args:
        population: List of individuals
        toolbox: deap.base.Toolbox with registered operators
        n_generations: Maximum number of generations (default: 100)
        n_elites: Number of elite individuals to preserve (default: 1)
        stats: deap.tools.Statistics object for tracking (optional)
        hall_of_fame: deap.tools.HallOfFame for best individuals (optional)
        verbose: Whether to print statistics (default: True)
        tolerance: Error tolerance for early termination (default: 1e-10)
        GEP_type: Name/identifier for the problem (default: '')
        check_interval: Generations between output checks (default: 20)
        termination_check_interval: Generations between termination checks (default: 100)
        output_dir: Directory for output files (default: 'output')
        pkl_dir: Directory for population files (default: 'pkl')
        evaluate_no_loss_entropy: Optional function to evaluate without entropy loss
        
    Returns:
        tuple: (final_population, logbook)
    """
    _validate_basic_toolbox(toolbox)
    logbook = deap.tools.Logbook()
    logbook.header = ['gen', 'nevals'] + (stats.fields if stats else [])
    start_time = time.time()

    # Create output directories if they don't exist
    os.makedirs(pkl_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
    simplified_best_list = []
    
    for gen in range(n_generations + 1):
        # Evaluate invalid individuals
        invalid_individuals = [ind for ind in population if not ind.fitness.valid]
        fitnesses = toolbox.map(toolbox.evaluate, invalid_individuals)
        for ind, fit in zip(invalid_individuals, fitnesses):
            ind.fitness.values = fit

        # Record statistics
        if hall_of_fame is not None:
            hall_of_fame.update(population)
        record = stats.compile(population) if stats else {}
        logbook.record(gen=gen, nevals=len(invalid_individuals), **record)
        if verbose:
            print(logbook.stream)

        if gen == n_generations:
            break

        # Selection with elitism
        elites = deap.tools.selBest(population, k=n_elites)
        offspring = toolbox.select(population, len(population) - n_elites)

        # Output real-time results
        if gen > 0 and gen % check_interval == 0:
            elites_IR = elites[0]
            simplified_best = gep.simplify(elites_IR)
            
            if str(simplified_best) not in simplified_best_list:
                simplified_best_list.append(str(simplified_best))
                elapsed = time.time() - start_time
                time_str = f'{elapsed:.2f}'
                
                output_file = os.path.join(output_dir, f'{GEP_type}_equation.dat')
                
                if elites_IR.a != 1e18:
                    simplified_best = elites_IR.a * simplified_best
                    key = f'In generation {gen}, with CPU running {time_str}s, \nOur No.1 best prediction is:'
                    
                    # Build output string
                    output_str = f'\n{key}{simplified_best}\nwith loss = {elites_IR.fitness.values[0]}'
                    
                    # Add entropy loss if evaluation function is provided
                    if evaluate_no_loss_entropy is not None:
                        try:
                            no_entropy_loss = evaluate_no_loss_entropy(elites_IR)[0]
                            output_str += f', no entropy loss = {no_entropy_loss}'
                        except Exception:
                            pass
                    
                    output_str += '\n'
                    
                    with open(output_file, "a") as f:
                        f.write(output_str)
                else:
                    key = f'In generation {gen}, with CPU running {time_str}s, \nOur No.1 best prediction is:'
                    with open(output_file, "a") as f:
                        f.write(f'\n{key}{simplified_best}\nwhich is invalid!\n')

        # Check termination criterion
        if gen > 0 and gen % termination_check_interval == 0:
            error_min = elites[0].fitness.values[0]
            if error_min < tolerance:
                pkl_file = os.path.join(pkl_dir, f'{GEP_type}.pkl')
                with open(pkl_file, 'wb') as f:
                    pickle.dump(population, f)
                break

        # Replication
        offspring = [toolbox.clone(ind) for ind in offspring]

        # Apply mutations
        for op in toolbox.pbs:
            if op.startswith('mut'):
                offspring = _apply_modification(offspring, getattr(toolbox, op), toolbox.pbs[op])

        # Apply crossover
        for op in toolbox.pbs:
            if op.startswith('cx'):
                offspring = _apply_crossover(offspring, getattr(toolbox, op), toolbox.pbs[op])

        # Replace population with offspring
        population = elites + offspring
    
    # Save final population
    pkl_file = os.path.join(pkl_dir, f'{GEP_type}.pkl')
    with open(pkl_file, 'wb') as f:
        pickle.dump(population, f)

    return population, logbook


__all__ = ['dimensional_verification', 'gep_simple', 'count_negative_numbers']
