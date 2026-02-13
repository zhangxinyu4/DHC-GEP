# coding=utf-8
"""
Simplified example of Diffusion Equation solving using DHC-GEP modular package.
"""

import random
import numpy as np
from fractions import Fraction
from deap import tools
import pickle
import sys
sys.path.insert(0, '..')

# Import the new modular dhc_gep package
import dhc_gep
from dhc_gep import L, M, T

# Set random seeds
SEED = 0
random.seed(SEED)
np.random.seed(SEED)

def main():
    # Load data
    print("Loading data...")
    data = dhc_gep.load_mat_data(
        filepath='../data/Diffusion_flow.mat',
        variable_names=['rho', 'rho_y', 'rho_yy', 'rho_3y', 'rho_t'],
        subsample=720,
        seed=SEED
    )
    
    input_vars = ['rho', 'rho_y', 'rho_yy', 'rho_3y']
    target_var = 'rho_t'
    X_data, y_data = dhc_gep.prepare_training_data(data, input_vars, target_var)
    
    # Physical constants
    diffusion_coef = 1.399e-05
    miu = 2.079e-5
    
    # Configuration
    print("Setting up configuration...")
    config = dhc_gep.get_config(
        head_length=15,
        n_genes=2,
        n_population=100,  # Smaller for demo
        n_generations=10,  # Fewer for demo
        tolerance=1e-3
    )
    
    # Dimensions
    dict_of_dimension = {
        'rho': Fraction(M, L**3),
        'rho_y': Fraction(M, L**4),
        'rho_yy': Fraction(M, L**5),
        'rho_3y': Fraction(M, L**6),
        'df_c': Fraction(L**2, T),
        'Miu': Fraction(M, L*T)
    }
    target_dimension = Fraction(M, T*L**3)
    
    # Create primitive set and toolbox
    print("Creating toolbox...")
    pset = dhc_gep.setup_primitive_set(
        input_names=input_vars,
        constants={'df_c': diffusion_coef, 'Miu': miu},
        operators='basic'
    )
    
    toolbox = dhc_gep.create_toolbox(pset, config)
    dhc_gep.register_genetic_operators(toolbox, config)
    
    # Evaluation function
    toolbox.register('dimensional_verification', dhc_gep.dimensional_verification)
    
    def evaluate_ls(individual):
        validity = toolbox.dimensional_verification(
            individual, dict_of_dimension, target_dimension
        )
        if not validity:
            individual.a = config['invalid_marker']
            return config['invalid_fitness'],
        
        func = toolbox.compile(individual)
        try:
            Yp = np.array(list(map(func, *X_data)))
        except (FloatingPointError, ZeroDivisionError):
            individual.a = config['invalid_marker']
            return config['invalid_fitness'],
        
        if isinstance(Yp, np.ndarray):
            Q = np.reshape(Yp, (-1, 1)).astype('float32')
            Q = np.nan_to_num(Q)
            individual.a, residuals, _, _ = np.linalg.lstsq(Q, y_data, rcond=None)
            c = individual.a.reshape(-1, 1)
            relative_error = (np.dot(Q, c) - y_data) / y_data
            if residuals.size > 0:
                return np.mean(np.abs(relative_error)),
        
        individual.a = 0
        relative_error = (y_data - individual.a) / y_data
        return np.mean(np.abs(relative_error)),
    
    toolbox.register('evaluate', evaluate_ls)
    
    # Statistics and Hall of Fame
    stats = dhc_gep.setup_statistics()
    hof = tools.HallOfFame(config['n_champions'])
    
    # Initialize population
    print("Initializing population...")
    population = toolbox.population(n=config['n_population'])
    
    # Run evolution
    print("\nStarting evolution...\n")
    population, logbook = dhc_gep.gep_simple(
        population=population,
        toolbox=toolbox,
        n_generations=config['n_generations'],
        n_elites=config['n_elites'],
        stats=stats,
        hall_of_fame=hof,
        verbose=config['verbose'],
        tolerance=config['tolerance'],
        GEP_type='Diffusion_example',
        check_interval=config['check_interval'],
        output_dir=config['output_dir'],
        pkl_dir=config['pkl_dir']
    )
    
    print("\nEvolution completed!")
    print(f"Best fitness: {hof[0].fitness.values[0]}")

if __name__ == '__main__':
    main()
