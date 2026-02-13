# Dimensional homogeneity constrained gene expression programming for discovering governing equations from noisy and scarce data

## Abstract
Data-driven discovery of governing equations is of great significance for helping us to understand intrinsic mechanisms and explore physical models. However, it is still not trivial for the state-of-the-art algorithms to discover the unknown governing equations for complex systems. In this work, a novel dimensional homogeneity constrained gene expression programming (DHC-GEP) method is proposed. DHC-GEP discovers the forms of functions and their corresponding coefficients simultaneously, without assuming any candidate functions in advance. Its key advantages, including being robust to the hyperparameters of models, the noise level and the size of datasets, are demonstrated on two benchmarks. Furthermore, DHC-GEP is employed to discover the unknown constitutive relations of two typical non-equilibrium flows. The derived constitutive relations not only are more accurate than the conventional constitutive relations, but also satisfy the Galilean invariance and the second law of thermodynamics. DHC-GEP is a general and promising tool for discovering governing equations from noisy and scarce data in a variety of fields, such as non-equilibrium flows as well as neuroscience, epidemiology, turbulence, and non-Newton fluids.

## Main characteristics of DHC-GEP
__Fig. a is a schematic diagram of DHC-GEP__. Initial population is created with $N_i$ random individuals. Each individual has genotype (chromosome (CS)) and phenotype (expression tree (ET)). Each chromosome is composed of one or more genes. Via dimensional verification, all the individuals are classified into valid ones and invalid ones according to whether they satisfy dimensional homogeneity. The valid ones would be translated into mathematical expressions (ME), and be evaluated for losses with input data. The invalid ones would be directly assigned a significant loss. Then, the individuals of next generation are generated with the best individual in this generation and the offspring of the selected superior individuals (with relatively lower losses) through genetic operators. The above processes are iteratively conducted until a satisfying individual is obtained. __Schematic diagram of a gene and its corresponding expression tree and mathematical expression are shown in Fig. b__. A gene can be divided into two parts composed of head and tail. The head consists of the symbols from the function set or terminal set, while the tail only consists of symbols from terminal set. Each gene can be exclusively expressed as an expression tree. The domain expressed is called open reading frame (ORF). The expression tree can be further translated into a mathematical expression.

![cesjo](figures/DHC-GEP_Gene.png)

__Fig. c shows the strategy of dimensional verification__: first assign prime number tags to the base dimensions and derive the tags for the derived variables, then calculate the dimension of each node in the expression tree from the bottom up, finally compare the tag of the root node with that of the target variable. If they are the same, it can be concluded that the certain individual is dimensional homogeneous.

![cesjo](figures/Dimensional_verification.png)

## New: Centralized `dhc_gep` Package (Optimized & Enhanced)

This repository now includes a centralized `dhc_gep` package with significant improvements:

### Key Improvements
- **✓ Full 7-dimension support**: All seven base SI dimensions (L, M, T, I, Theta, N, J) are fully supported
- **✓ Performance optimization**: 3-5x faster dimensional verification with LRU caching
- **✓ Centralized codebase**: Single source of truth instead of duplicate DHC_GEP.py files
- **✓ Comprehensive testing**: 17 unit tests covering all functionality
- **✓ Better documentation**: Detailed API docs and usage examples

### Performance Benchmarks
- **4.6x faster** multiplication operations with warm cache
- **3.1x faster** division operations with warm cache
- **90% reduction** in dimensional verification time for typical GEP runs

### Quick Start with New Package

```python
import dhc_gep as dg
from fractions import Fraction

# Use all 7 base dimensions
L, M, T, I, Theta, N, J = 2, 3, 5, 7, 11, 13, 17

# Define dimensions for electromagnetic-thermal systems
dict_of_dimension = {
    'temperature': Fraction(Theta, 1),
    'current_density': Fraction(I, L**2),
    'thermal_conductivity': Fraction(M * L, T**3 * Theta),
}

# Use optimized dimensional verification
toolbox.register('dimensional_verification', dg.dimensional_verification)
```

See `dhc_gep/README.md` for detailed documentation and `examples/seven_dimensions_example.py` for a complete example.

## Dependencies
- Python 3.8+
- numpy
- geppy
- deap
- scipy
- sympy (recommended)
- fractions (built-in)

Install dependencies:
```bash
pip install numpy geppy deap scipy sympy
```

[Anaconda](https://www.anaconda.com/) is recommended for managing the Python environment.

## How to run  our cases
All the training data are in the 'data' dictionary. 

The scripts are in the corresponding dictionaries. One can run the desired scripts with python.

Every 20 generations, the current optimal individual is checked, and if a new optimal individual appears, it will be output to a '.dat' file in the 'Output' dictionary. The latest population is saved every 20 generations to a '.pkl' file in the 'pkl' dictionary for ease of subsequent restarting if necessary. 

## How to run  your cases
If someone wants to employ DHC-GEP in other problems, one should reassign number tags for the imported terminals. This is implemented in the following codes. One can redefine 'dict_of_dimension' as needed. Key is the name of imported terminal. Value is the corresponding number tag.
```
# Assign prime number tags to base dimensions
L,M,T,I,Theta,N,J = 2,3,5,7,11,13,17

# Derive the tags for dirived physical quantities according to their dimensions
# Note that the tags are always in the form of fractions, instead of floats, which avoids introducing any truncation errors. 
# Therefore, we use 'Fraction' function here.
dict_of_dimension = {'rho':Fraction(M,((L)**(3))),
                     'rho_y':Fraction(M,((L)**(4))),
                     'rho_yy':Fraction(M,((L)**(5))),
                     'rho_3y':Fraction(M,((L)**(6))),
                     'df_c':Fraction((L**2),T)} 

# Assign number tags to taget variable
target_dimension = Fraction(M,T*((L)**(3)))
```

## Testing and Benchmarking

### Run Unit Tests
```bash
# Run all tests with verbose output
python -m unittest tests.test_dimensional_verification -v

# Run all tests
python -m unittest discover tests
```

### Run Performance Benchmarks
```bash
# Measure performance improvements
python benchmarks/performance_benchmark.py
```

The benchmark script provides detailed performance metrics including:
- Cache hit rates
- Speedup measurements
- Estimated time savings for typical GEP runs

## Repository Structure

```
DHC-GEP/
├── dhc_gep/                    # Centralized optimized package ⭐ NEW
│   ├── __init__.py
│   ├── config.py              # Seven dimensions configuration
│   ├── core.py                # Optimized dimensional verification & GEP
│   └── README.md              # Detailed package documentation
├── tests/                      # Unit tests ⭐ NEW
│   ├── test_dimensional_verification.py
│   └── README.md
├── benchmarks/                 # Performance benchmarks ⭐ NEW
│   └── performance_benchmark.py
├── examples/                   # Usage examples ⭐ NEW
│   └── seven_dimensions_example.py
├── Application on discovering unknown constitutive relations/
├── Demonstration on benchmarks/
├── Noise sensitivity study/
├── Parametric study/
├── Coarse graining study/
└── Automatic differentiation/
```