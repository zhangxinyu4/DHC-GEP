"""
Example demonstrating the use of all 7 base dimensions in DHC-GEP.

This example shows how to use:
- L (Length): 2
- M (Mass): 3
- T (Time): 5
- I (Electric Current): 7
- Theta (Temperature): 11
- N (Amount of Substance): 13
- J (Luminous Intensity): 17

Physical scenario: Electromagnetic heat transfer problem
Target: Finding the rate of temperature change with electromagnetic effects
"""

import geppy as gep
from deap import creator, base, tools
import numpy as np
import random
import operator
from fractions import Fraction
import sys
import os

# Add parent directory to path to import dhc_gep
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import dhc_gep as dg

# For reproduction
s = 0
random.seed(s)
np.random.seed(s)

print("="*80)
print("DHC-GEP: Seven Dimensions Example")
print("="*80)
print("\nThis example demonstrates dimensional verification using all 7 base dimensions:")
print("  L (Length): 2")
print("  M (Mass): 3")
print("  T (Time): 5")
print("  I (Electric Current): 7")
print("  Theta (Temperature): 11")
print("  N (Amount of Substance): 13")
print("  J (Luminous Intensity): 17")
print("="*80)

# %% Assign number tags for all 7 dimensions

# Assign prime number tags to base dimensions
L, M, T, I, Theta, N, J = 2, 3, 5, 7, 11, 13, 17

# Physical quantities in an electromagnetic-thermal-chemical system:
# 
# Example variables demonstrating all 7 dimensions:
# - density (rho): M/L³
# - velocity (v): L/T
# - temperature (temp): Theta
# - current_density (j): I/L²
# - heat_capacity (c_p): L²/(T²·Theta)
# - molar_concentration (c): N/L³
# - luminous_flux_density (phi): J/L²
# - thermal_conductivity (k): M·L/(T³·Theta)

dict_of_dimension = {
    'rho': Fraction(M, L**3),                    # Density: kg/m³
    'v': Fraction(L, T),                          # Velocity: m/s
    'temp': Fraction(Theta, 1),                   # Temperature: K
    'j': Fraction(I, L**2),                       # Current density: A/m²
    'c_p': Fraction(L**2, T**2 * Theta),         # Specific heat capacity: m²/(s²·K)
    'c': Fraction(N, L**3),                       # Molar concentration: mol/m³
    'phi': Fraction(J, L**2),                     # Luminous flux density: cd/m²
    'k': Fraction(M * L, T**3 * Theta),          # Thermal conductivity: kg·m/(s³·K)
}

# Target: Rate of temperature change (dT/dt) in K/s
# Dimension: Theta/T
target_dimension = Fraction(Theta, T)

print("\nVariable Dimensions:")
for var, dim in dict_of_dimension.items():
    print(f"  {var:10s}: {dim}")
print(f"\nTarget dimension (dT/dt): {target_dimension}")
print("="*80)

# %% Generate synthetic data for demonstration
# In a real scenario, this would be experimental or simulation data

np.random.seed(s)
n_samples = 100

# Generate synthetic data
rho_data = np.random.uniform(900, 1100, (n_samples, 1))      # Density
v_data = np.random.uniform(0.1, 2.0, (n_samples, 1))         # Velocity
temp_data = np.random.uniform(273, 373, (n_samples, 1))      # Temperature
j_data = np.random.uniform(0, 1000, (n_samples, 1))          # Current density
c_p_data = np.random.uniform(4000, 5000, (n_samples, 1))     # Heat capacity
c_data = np.random.uniform(0.1, 10, (n_samples, 1))          # Concentration
phi_data = np.random.uniform(0, 100, (n_samples, 1))         # Luminous flux
k_data = np.random.uniform(0.5, 2.0, (n_samples, 1))         # Thermal conductivity

# Target: A synthetic relationship (for demonstration)
# Real formula: dT/dt ≈ k/(rho * c_p) (simplified heat equation term)
Y = (k_data / (rho_data * c_p_data))  # This has dimension Theta/T

print(f"\nGenerated {n_samples} synthetic data points")
print(f"Data ranges:")
print(f"  rho: [{rho_data.min():.2f}, {rho_data.max():.2f}] kg/m³")
print(f"  v: [{v_data.min():.2f}, {v_data.max():.2f}] m/s")
print(f"  temp: [{temp_data.min():.2f}, {temp_data.max():.2f}] K")
print(f"  j: [{j_data.min():.2f}, {j_data.max():.2f}] A/m²")
print(f"  c_p: [{c_p_data.min():.2f}, {c_p_data.max():.2f}] J/(kg·K)")
print(f"  c: [{c_data.min():.2f}, {c_data.max():.2f}] mol/m³")
print(f"  phi: [{phi_data.min():.2f}, {phi_data.max():.2f}] cd/m²")
print(f"  k: [{k_data.min():.2f}, {k_data.max():.2f}] W/(m·K)")
print("="*80)

# %% Creating the primitives set

def protected_div(x1, x2):
    """Protected division to avoid dividing by zero."""
    if abs(x2) < 1e-10:
        return 1
    return x1 / x2

# Define the operators
pset = gep.PrimitiveSet('Main', input_names=['rho', 'v', 'temp', 'j', 'c_p', 'c', 'phi', 'k'])
pset.add_function(operator.add, 2)
pset.add_function(operator.sub, 2)
pset.add_function(operator.mul, 2)
pset.add_function(protected_div, 2)

# %% Create the individual and population

creator.create("FitnessMin", base.Fitness, weights=(-1,))
creator.create("Individual", gep.Chromosome, fitness=creator.FitnessMin)

# GEP parameters
h = 10              # head length
n_genes = 2         # number of genes in a chromosome
enable_ls = True    # whether to apply the linear scaling technique

toolbox = gep.Toolbox()
toolbox.register('gene_gen', gep.Gene, pset=pset, head_length=h)
toolbox.register('individual', creator.Individual, gene_gen=toolbox.gene_gen, n_genes=n_genes, linker=operator.add)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register('compile', gep.compile_, pset=pset)

# %% Define the loss function

# Register the dimensional verification operation using the optimized version
toolbox.register('dimensional_verification', dg.dimensional_verification)

def evaluate(individual):
    """
    Evaluate an individual with dimensional verification.
    """
    # First check dimensional homogeneity
    if not toolbox.dimensional_verification(individual, dict_of_dimension, target_dimension, use_protected_div=True):
        return 1e18,  # Large penalty for dimensionally invalid individuals
    
    # Compile and evaluate
    func = toolbox.compile(individual)
    
    try:
        # Evaluate the function
        Yp = np.array([func(rho_data[i, 0], v_data[i, 0], temp_data[i, 0], j_data[i, 0],
                           c_p_data[i, 0], c_data[i, 0], phi_data[i, 0], k_data[i, 0])
                      for i in range(len(Y))])
        Yp = Yp.reshape(-1, 1)
        
        # Handle invalid results
        if np.isnan(Yp).any() or np.isinf(Yp).any():
            return 1e18,
        
        # Compute loss (MSE)
        loss = np.mean((Y - Yp) ** 2)
        return loss,
    except:
        return 1e18,

toolbox.register('evaluate', evaluate)

# %% Register genetic operators
toolbox.register('select', tools.selTournament, tournsize=3)

# 1. general operators
toolbox.register('mut_uniform', gep.mutate_uniform, pset=pset, ind_pb=0.05, pb=1)
toolbox.register('cx_1p', gep.crossover_one_point, pb=0.1)

# 2. Dc-specific operators
toolbox.pbs = {'mut_uniform': 0.2, 'cx_1p': 0.5}

# %% Statistics and Hall of Fame
stats = tools.Statistics(key=lambda ind: ind.fitness.values[0])
stats.register("avg", np.mean)
stats.register("std", np.std)
stats.register("min", np.min)
stats.register("max", np.max)

# Hall of fame to store the best individuals
hof = tools.HallOfFame(3)

# %% Run evolution (short demonstration)
print("\nRunning GEP evolution with dimensional verification...")
print("This is a short demonstration run with 50 generations.")
print("="*80)

n_pop = 30
n_gen = 50
champs = 3

pop = toolbox.population(n=n_pop)
pop, log = dg.gep_simple(pop, toolbox, n_generations=n_gen, n_elites=champs,
                         stats=stats, hall_of_fame=hof, verbose=True,
                         tolerance=1e-6, GEP_type='seven_dimensions')

print("="*80)
print("\nEvolution completed!")
print(f"\nBest individual found:")
best_ind = hof[0]
print(f"  Expression: {gep.simplify(best_ind)}")
print(f"  Fitness: {best_ind.fitness.values[0]:.6e}")
print(f"  Dimensionally valid: {toolbox.dimensional_verification(best_ind, dict_of_dimension, target_dimension, use_protected_div=True)}")
print("="*80)

# %% Verify dimensions are being used
print("\nDimensional Analysis Summary:")
print(f"  Total base dimensions available: 7 (L, M, T, I, Theta, N, J)")
print(f"  Variables using these dimensions: {len(dict_of_dimension)}")
print(f"  Dimensions represented in variables:")

# Check which base dimensions are actually used
dims_used = set()
for var, dim in dict_of_dimension.items():
    # Factor the dimension to find base dimensions
    num_factors = []
    den_factors = []
    
    # Check numerator and denominator
    if dim.numerator % 2 == 0 or dim.denominator % 2 == 0:
        dims_used.add('L (Length)')
    if dim.numerator % 3 == 0 or dim.denominator % 3 == 0:
        dims_used.add('M (Mass)')
    if dim.numerator % 5 == 0 or dim.denominator % 5 == 0:
        dims_used.add('T (Time)')
    if dim.numerator % 7 == 0 or dim.denominator % 7 == 0:
        dims_used.add('I (Current)')
    if dim.numerator % 11 == 0 or dim.denominator % 11 == 0:
        dims_used.add('Theta (Temperature)')
    if dim.numerator % 13 == 0 or dim.denominator % 13 == 0:
        dims_used.add('N (Substance)')
    if dim.numerator % 17 == 0 or dim.denominator % 17 == 0:
        dims_used.add('J (Luminosity)')

for dim in sorted(dims_used):
    print(f"    ✓ {dim}")

print(f"\n  Total unique base dimensions used: {len(dims_used)}/7")
print("="*80)

print("\n✅ Successfully demonstrated DHC-GEP with all 7 base dimensions!")
