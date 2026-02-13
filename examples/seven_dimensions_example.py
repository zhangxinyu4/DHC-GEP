# %% Example demonstrating all 7 SI base dimensions
"""
This example demonstrates the full capability of DHC-GEP to handle all 7 SI base dimensions:
- L (Length) - meter [m]
- M (Mass) - kilogram [kg]
- T (Time) - second [s]
- I (Electric Current) - ampere [A]
- Theta (Temperature) - kelvin [K]
- N (Amount of Substance) - mole [mol]
- J (Luminous Intensity) - candela [cd]

Physical example: Thermal conductivity in a thermoelectric material
Target equation: heat_flux = thermal_conductivity * temperature_gradient
"""

import geppy as gep
from deap import creator, base, tools
import numpy as np
import random
import operator 
from fractions import Fraction
import sys
import os

# Add parent directory to path to import DHC_GEP
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import DHC_GEP as dg

# For reproduction
s = 0
random.seed(s)
np.random.seed(s)

# %% Generate synthetic data
# Simulating thermoelectric behavior: q = k * grad_T + Seebeck_coef * I * T

n_samples = 100

# Input variables with proper physical units
temperature = np.random.uniform(250, 350, n_samples)  # Temperature [K]
temp_gradient = np.random.uniform(-10, 10, n_samples)  # Temperature gradient [K/m]
current = np.random.uniform(0, 5, n_samples)  # Electric current [A]
material_density = np.random.uniform(5000, 8000, n_samples)  # Density [kg/m³]
molar_mass = np.random.uniform(0.05, 0.1, n_samples)  # Molar mass [kg/mol]
luminous_flux_per_area = np.random.uniform(100, 200, n_samples)  # Luminous flux density [cd/m²]

# Physical constants with units
thermal_conductivity = 50.0  # [W/(m·K)] = [kg·m/(s³·K)]
seebeck_coefficient = 200e-6  # [V/K] = [kg·m²/(s³·A·K)]

# Target: Heat flux density [W/m²] = [kg/s³]
# Using simplified thermoelectric equation: q = k * grad_T
heat_flux = thermal_conductivity * temp_gradient

# Add some noise
heat_flux = heat_flux + np.random.normal(0, 0.5, n_samples)

# Reshape for GEP
temperature = temperature.reshape(-1, 1)
temp_gradient = temp_gradient.reshape(-1, 1)
current = current.reshape(-1, 1)
material_density = material_density.reshape(-1, 1)
molar_mass = molar_mass.reshape(-1, 1)
luminous_flux_per_area = luminous_flux_per_area.reshape(-1, 1)
Y = heat_flux.reshape(-1, 1)

# %% Assign number tags for all 7 SI base dimensions

# Assign prime number tags to all 7 base dimensions
L, M, T, I, Theta, N, J = 2, 3, 5, 7, 11, 13, 17

print("=" * 60)
print("Seven SI Base Dimensions with Prime Number Encoding:")
print("=" * 60)
print(f"L (Length):              {L}")
print(f"M (Mass):                {M}")
print(f"T (Time):                {T}")
print(f"I (Electric Current):    {I}")
print(f"Theta (Temperature):     {Theta}")
print(f"N (Amount of Substance): {N}")
print(f"J (Luminous Intensity):  {J}")
print("=" * 60)

# Define dimensions for each physical quantity
# Temperature: [K] = [Theta]
# Temperature gradient: [K/m] = [Theta/L]
# Electric current: [A] = [I]
# Material density: [kg/m³] = [M/L³]
# Molar mass: [kg/mol] = [M/N]
# Luminous flux per area: [cd/m²] = [J/L²]
# Thermal conductivity constant: [W/(m·K)] = [kg·m/(s³·K)] = [M·L/(T³·Theta)]

dict_of_dimension = {
    'temperature': Fraction(Theta),
    'temp_gradient': Fraction(Theta, L),
    'current': Fraction(I),
    'density': Fraction(M, L**3),
    'molar_mass': Fraction(M, N),
    'luminous': Fraction(J, L**2),
    'k_thermal': Fraction(M * L, T**3 * Theta)  # Thermal conductivity
}

# Target dimension: Heat flux [W/m²] = [kg/s³] = [M/T³]
target_dimension = Fraction(M, T**3)

print("\nDimensional Analysis:")
print("=" * 60)
for name, dim in dict_of_dimension.items():
    print(f"{name:20s}: {dim}")
print(f"{'Target (heat_flux)':20s}: {target_dimension}")
print("=" * 60)

# %% Creating the primitives set
def protected_div(x1, x2):
    """Protected division to avoid dividing by zero"""
    if abs(x2) < 1e-10:
        return 1
    return x1 / x2

# Define the operators
pset = gep.PrimitiveSet('Main', input_names=['temperature', 'temp_gradient', 'current', 
                                               'density', 'molar_mass', 'luminous'])
pset.add_symbol_terminal('k_thermal', thermal_conductivity)
pset.add_function(operator.add, 2)
pset.add_function(operator.sub, 2)
pset.add_function(operator.mul, 2)
pset.add_function(operator.truediv, 2)
pset.add_rnc_terminal()  # Add random numerical constants (RNC)
np.seterr(divide='raise')

# %% Create the individual and population

# Define the individual class
creator.create("FitnessMin", base.Fitness, weights=(-1,))
creator.create("Individual", gep.Chromosome, fitness=creator.FitnessMin)

# Register the individual and population creation operations
h = 10            # head length
n_genes = 2       # number of genes in a chromosome
r = 10            # length of the RNC array
enable_ls = True  # whether to apply the linear scaling technique

toolbox = gep.Toolbox()
toolbox.register('rnc_gen', random.randint, a=-5, b=5)
toolbox.register('gene_gen', gep.GeneDc, pset=pset, head_length=h, rnc_gen=toolbox.rnc_gen, rnc_array_length=r)
toolbox.register('individual', creator.Individual, gene_gen=toolbox.gene_gen, n_genes=n_genes, linker=operator.add)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register('compile', gep.compile_, pset=pset)

# %% Define the loss function

# Register the dimensional verification operation
toolbox.register('dimensional_verification', dg.dimensional_verification)

def evaluate_ls(individual):
    """
    Evaluate fitness with dimensional verification and linear scaling.
    """
    validity = toolbox.dimensional_verification(individual, dict_of_dimension, target_dimension)
    if not validity:
        individual.a = 1e18
        return 1000,
    else:
        func = toolbox.compile(individual)
        try:
            Yp = np.array(list(map(func, temperature, temp_gradient, current, 
                                   density, molar_mass, luminous)))
        except (FloatingPointError, ZeroDivisionError):
            individual.a = 1e18
            return 1000,
        
        if isinstance(Yp, np.ndarray):
            Q = (np.reshape(Yp, (-1, 1))).astype('float32')
            Q = np.nan_to_num(Q)
            individual.a, residuals, _, _ = np.linalg.lstsq(Q, Y, rcond=None)

            # Define the mean relative error (MRE)
            c = individual.a.reshape(-1, 1)
            relative_error = (np.dot(Q, c) - Y) / (Y + 1e-10)
            if residuals.size > 0:
                return np.mean(abs(relative_error)),
        
        individual.a = 0
        relative_error = (Y - individual.a) / (Y + 1e-10)
        return np.mean(abs(relative_error)),

toolbox.register('evaluate', evaluate_ls)

# %% Register genetic operators
toolbox.register('select', tools.selTournament, tournsize=3)
# 1. general operators
toolbox.register('mut_uniform', gep.mutate_uniform, pset=pset, ind_pb=0.05, pb=1)
toolbox.register('mut_invert', gep.invert, pb=0.1)
toolbox.register('mut_is_transpose', gep.is_transpose, pb=0.1)
toolbox.register('mut_ris_transpose', gep.ris_transpose, pb=0.1)
toolbox.register('mut_gene_transpose', gep.gene_transpose, pb=0.1)
toolbox.register('cx_1p', gep.crossover_one_point, pb=0.3)
toolbox.register('cx_2p', gep.crossover_two_point, pb=0.2)
toolbox.register('cx_gene', gep.crossover_gene, pb=0.1)
# 2. Dc-specific operators
toolbox.register('mut_dc', gep.mutate_uniform_dc, ind_pb=0.05, pb=1)
toolbox.register('mut_invert_dc', gep.invert_dc, pb=0.1)
toolbox.register('mut_transpose_dc', gep.transpose_dc, pb=0.1)
toolbox.register('mut_rnc_array_dc', gep.mutate_rnc_array_dc, rnc_gen=toolbox.rnc_gen, ind_pb='0.5p')
toolbox.pbs['mut_rnc_array_dc'] = 1

# %% Statistics to be inspected
stats = tools.Statistics(key=lambda ind: ind.fitness.values[0])
stats.register("avg", np.mean)
stats.register("std", np.std)
stats.register("min", np.min)
stats.register("max", np.max)

# %% Launch evolution
if __name__ == '__main__':
    print("\nStarting GEP evolution with 7-dimensional constraint...")
    print("=" * 60)
    
    n_pop = 100               # Number of individuals in a population
    n_gen = 50                # Maximum Generation (small for demonstration)
    tol = 1e-2                # Threshold to terminate the evolution
    output_type = 'Seven_Dimensions_Example'
    
    pop = toolbox.population(n=n_pop)
    
    # Only record the best three individuals
    champs = 3
    hof = tools.HallOfFame(champs)
    
    # Evolve
    pop, log = dg.gep_simple(pop, toolbox, n_generations=n_gen, n_elites=1,
                             stats=stats, hall_of_fame=hof, verbose=True,
                             tolerance=tol, GEP_type=output_type)
    
    print("\n" + "=" * 60)
    print("Evolution Complete!")
    print("=" * 60)
    print("\nBest individuals:")
    for i, ind in enumerate(hof):
        print(f"\n#{i+1} (fitness: {ind.fitness.values[0]:.6f}):")
        print(f"  Expression: {gep.simplify(ind)}")
        if hasattr(ind, 'a') and ind.a != 1e18:
            print(f"  With coefficient: {ind.a[0]:.6f}")
    
    print("\n" + "=" * 60)
    print("This example demonstrates DHC-GEP's capability to handle")
    print("all 7 SI base dimensions simultaneously!")
    print("=" * 60)
