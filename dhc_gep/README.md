# DHC-GEP Package

Modular and configurable implementation of Dimensional Homogeneity Constrained Gene Expression Programming (DHC-GEP).

## Overview

This package provides a refactored, maintainable implementation of the DHC-GEP algorithm with the following improvements:

- **No Code Duplication**: Single source of truth for all core functionality
- **Configurable Parameters**: Centralized configuration management
- **Modular Design**: Separate modules for different concerns
- **Easy to Use**: Simple API with sensible defaults
- **Well Documented**: Comprehensive docstrings and examples

## Modules

### `config.py`
Centralized configuration management for all DHC-GEP parameters:
- Default algorithm parameters
- Parametric study ranges
- Dimensional definitions
- Configuration helper functions

### `core.py`
Core DHC-GEP functionality:
- `dimensional_verification()`: Check dimensional homogeneity
- `gep_simple()`: Enhanced GEP evolution with monitoring and auto-save
- `count_negative_numbers()`: Utility function

### `utils.py`
Utility functions for experiment setup:
- `setup_primitive_set()`: Create primitive sets with operators
- `create_toolbox()`: Initialize GEP toolbox
- `register_genetic_operators()`: Configure genetic operators
- `setup_statistics()`: Create statistics tracking
- `protected_division()`: Safe division operator

### `data_utils.py`
Data loading and preprocessing:
- `load_mat_data()`: Load MATLAB data files
- `prepare_training_data()`: Format data for training
- `normalize_data()`: Data normalization utilities
- `DataLoader`: Convenience class for data management

## Quick Start

```python
import dhc_gep
from dhc_gep import L, M, T
from fractions import Fraction

# 1. Load data
data = dhc_gep.load_mat_data(
    'data/Diffusion_flow.mat',
    ['rho', 'rho_y', 'rho_yy', 'rho_3y', 'rho_t'],
    subsample=720
)
X_data, y_data = dhc_gep.prepare_training_data(
    data, 
    input_vars=['rho', 'rho_y', 'rho_yy', 'rho_3y'],
    target_var='rho_t'
)

# 2. Configure
config = dhc_gep.get_config(
    n_population=1660,
    n_generations=200,
    tolerance=1e-3
)

# 3. Setup primitive set
pset = dhc_gep.setup_primitive_set(
    input_names=['rho', 'rho_y', 'rho_yy', 'rho_3y'],
    constants={'df_c': 1.399e-05}
)

# 4. Create toolbox and register operators
toolbox = dhc_gep.create_toolbox(pset, config)
dhc_gep.register_genetic_operators(toolbox, config)

# 5. Register evaluation function
toolbox.register('evaluate', your_evaluation_function)

# 6. Run evolution
from deap import tools
stats = dhc_gep.setup_statistics()
hof = tools.HallOfFame(3)
pop = toolbox.population(n=config['n_population'])

pop, log = dhc_gep.gep_simple(
    pop, toolbox,
    n_generations=config['n_generations'],
    stats=stats,
    hall_of_fame=hof,
    tolerance=config['tolerance'],
    GEP_type='my_experiment'
)
```

## Configuration

All default parameters are defined in `config.py`. You can override them:

```python
# Use defaults
config = dhc_gep.get_config()

# Override specific parameters
config = dhc_gep.get_config(
    head_length=10,
    n_genes=3,
    n_population=2000,
    mut_uniform_ind_pb=0.1
)
```

## Dimensional Verification

Define dimensions using Fractions to avoid floating-point errors:

```python
from fractions import Fraction
from dhc_gep import L, M, T

# Define variable dimensions
dims = {
    'density': Fraction(M, L**3),
    'velocity': Fraction(L, T),
    'pressure': Fraction(M, L*T**2)
}

# Or use common dimension sets
dims = dhc_gep.get_dimension_dict('diffusion')
```

## Benefits Over Original Implementation

### Before (Original)
- 5 copies of DHC_GEP.py with inconsistencies
- 27 example scripts with 80-90% duplicate code
- ~5000 lines of duplicated code
- Hardcoded parameters throughout
- No configuration management

### After (Refactored)
- Single source of truth in `dhc_gep/` package
- ~200 lines per example script (vs ~250 before)
- Centralized configuration
- Easy parameter tuning
- Maintainable and extensible

## Examples

See `examples/diffusion_equation_simplified.py` for a complete working example.

## Migration Guide

To migrate existing scripts to use the new package:

1. Import the package: `import dhc_gep`
2. Replace `import DHC_GEP as dg` with `import dhc_gep`
3. Use `dhc_gep.get_config()` instead of hardcoded parameters
4. Use helper functions like `setup_primitive_set()` and `create_toolbox()`
5. Replace `dg.dimensional_verification()` with `dhc_gep.dimensional_verification()`
6. Replace `dg.gep_simple()` with `dhc_gep.gep_simple()`

## License

Same as the original DHC-GEP project.
