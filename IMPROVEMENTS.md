# DHC-GEP Improvements: Dimensional Constraint Logic

## Overview
This document describes the improvements made to the DHC-GEP (Dimensional Homogeneity Constrained Gene Expression Programming) dimensional constraint logic to address:
1. Limited dimensional usage (previously only 3 dimensions used in practice)
2. Performance issues in dimensional verification
3. Code duplication across study directories

## Changes Made

### 1. Centralized DHC_GEP Module
**Location**: `/DHC_GEP.py`

A centralized module has been created at the repository root to:
- Eliminate code duplication (5 identical copies across different study directories)
- Provide a single source of truth for dimensional verification logic
- Simplify maintenance and future improvements

**Benefits**:
- Easier to update and maintain
- Consistent behavior across all examples
- Reduced repository size

### 2. Enhanced Dimensional Verification Function

The `dimensional_verification()` function has been improved with:

#### Performance Optimizations
- **Dimension result caching**: Results are cached using a dictionary to avoid redundant calculations for identical sub-expressions
- **Cache management**: Automatic cache clearing when it exceeds 10,000 entries to prevent memory issues
- **Improved structure**: Better code organization with helper functions

#### Maintained Backward Compatibility
- Original eval()-based implementation preserved as fallback
- All existing examples work without modification
- Same API and behavior as before

### 3. Full 7-Dimension Support Documentation

The system already supported all 7 SI base dimensions, but this was not well-documented. Now includes:

**Prime Number Encoding for All 7 SI Base Dimensions**:
```python
L = 2        # Length [m]
M = 3        # Mass [kg]
T = 5        # Time [s]
I = 7        # Electric Current [A]
Theta = 11   # Temperature [K]
N = 13       # Amount of Substance [mol]
J = 17       # Luminous Intensity [cd]
```

**Key Properties**:
- Each dimension assigned a unique prime number
- Dimensional products are uniquely identifiable
- Fraction-based computation avoids floating-point errors
- Supports arbitrary dimensional combinations

### 4. Comprehensive Examples and Tests

#### New Example: `examples/seven_dimensions_example.py`
A complete working example demonstrating:
- Usage of all 7 SI base dimensions simultaneously
- Thermoelectric system modeling (heat flux, temperature, electric current)
- Proper dimension assignment for complex physical quantities
- GEP evolution with multi-dimensional constraints

**Physical Quantities Demonstrated**:
- Temperature [Theta]
- Temperature gradient [Theta/L]
- Electric current [I]
- Material density [M/L³]
- Molar mass [M/N]
- Luminous flux density [J/L²]
- Thermal conductivity [M·L/(T³·Theta)]
- Heat flux [M/T³]

#### Unit Tests: `tests/test_dimensional_verification.py`
11 comprehensive unit tests covering:
- Basic L, M, T dimensions
- Electric current (I) dimension
- Temperature (Theta) dimension
- Amount of substance (N) dimension
- Luminous intensity (J) dimension
- All 7 dimensions simultaneously
- Addition/subtraction constraints (same dimensions required)
- Multiplication/division operations
- Dimensionless constants
- Complex nested expressions
- Cache performance

**Test Results**: All 11 tests pass ✓

## Technical Details

### Dimensional Verification Algorithm

The algorithm verifies dimensional homogeneity through:

1. **Prime Number Factorization**: Each dimension uses a unique prime number, making dimensional products uniquely factorizable
2. **Fraction Arithmetic**: Uses Python's `fractions.Fraction` to avoid floating-point errors
3. **Expression Evaluation**: Recursively evaluates dimension of each node in expression tree
4. **Constraint Rules**:
   - Addition/Subtraction: Operands must have identical dimensions
   - Multiplication: Dimensions multiply (exponents add)
   - Division: Dimensions divide (exponents subtract)
   - Constants: Treated as dimensionless (dimension = 1)

### Example Dimensional Calculation

For `heat_flux = thermal_conductivity * temperature_gradient`:

```python
# Thermal conductivity [W/(m·K)]
k_dim = Fraction(M * L, T**3 * Theta)  # = M·L/(T³·Theta)

# Temperature gradient [K/m]
grad_T_dim = Fraction(Theta, L)  # = Theta/L

# Product
heat_flux_dim = k_dim * grad_T_dim
             = [M·L/(T³·Theta)] * [Theta/L]
             = M/(T³)  # Correct! [W/m²]
```

### Performance Improvements

#### Before Optimization
- String replacement for every evaluation: `O(n)` per individual
- Dynamic code evaluation via `eval()`: ~100x slower than direct execution
- No memoization: Redundant calculations for identical sub-expressions

#### After Optimization
- Results cached: `O(1)` for repeated sub-expressions
- Cache size management: Prevents memory issues
- Maintained compatibility: Original implementation as fallback

**Expected Performance Gain**: 
- For typical GEP runs with 1000+ individuals over 100+ generations
- Estimated 10-30% reduction in dimensional verification time
- Greater improvement for expressions with repeated sub-structures

## Migration Guide

### For New Projects
Simply import the centralized module:
```python
import DHC_GEP as dg
```

### For Existing Projects
No changes required! The centralized module is backward compatible.

Optionally, you can:
1. Remove local `DHC_GEP.py` copies from study directories
2. Add parent directory to Python path if needed:
   ```python
   import sys
   import os
   sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
   import DHC_GEP as dg
   ```

## Usage Examples

### Mechanical Systems (L, M, T)
```python
L, M, T = 2, 3, 5
dict_of_dimension = {
    'velocity': Fraction(L, T),           # [m/s]
    'density': Fraction(M, L**3),         # [kg/m³]
    'force': Fraction(M * L, T**2)        # [N] = [kg·m/s²]
}
target_dimension = Fraction(M, L**2 * T)  # Momentum flux [kg/(m²·s)]
```

### Electromagnetic Systems (L, M, T, I)
```python
L, M, T, I = 2, 3, 5, 7
dict_of_dimension = {
    'current': Fraction(I),                      # [A]
    'voltage': Fraction(M * L**2, T**3 * I),     # [V]
    'resistance': Fraction(M * L**2, T**3 * I**2) # [Ω]
}
target_dimension = Fraction(M * L**2, T**3)      # Power [W]
```

### Thermodynamic Systems (L, M, T, Theta)
```python
L, M, T, Theta = 2, 3, 5, 11
dict_of_dimension = {
    'temperature': Fraction(Theta),                    # [K]
    'heat_capacity': Fraction(M * L**2, T**2 * Theta), # [J/K]
    'thermal_cond': Fraction(M * L, T**3 * Theta)      # [W/(m·K)]
}
target_dimension = Fraction(M * L**2, T**2)            # Energy [J]
```

### Chemical Systems (L, M, T, N)
```python
L, M, T, N = 2, 3, 5, 13
dict_of_dimension = {
    'amount': Fraction(N),                     # [mol]
    'molar_mass': Fraction(M, N),              # [kg/mol]
    'concentration': Fraction(N, L**3),        # [mol/m³]
    'reaction_rate': Fraction(N, L**3 * T)     # [mol/(m³·s)]
}
target_dimension = Fraction(M)                 # Mass [kg]
```

## Validation

### Unit Tests
All 11 unit tests pass, covering:
- Individual dimension functionality
- Combined dimension operations
- Edge cases and error conditions
- Performance characteristics

### Backward Compatibility
- Tested with existing diffusion equation example
- Verified all dimensional constraint patterns work correctly
- Confirmed no regression in functionality

### Example Execution
The 7-dimension example runs successfully, demonstrating:
- Proper dimensional verification
- GEP evolution with multi-dimensional constraints
- Output of valid mathematical expressions

## Future Enhancements

Potential improvements for future versions:

1. **Tree-based Evaluation**: Direct traversal of GEP expression trees instead of string manipulation (framework prepared in code)
2. **Parallel Evaluation**: Dimensional verification could be parallelized for large populations
3. **Advanced Caching**: Persistent cache across generations with LRU eviction
4. **Extended Physics**: Support for derived SI units and other unit systems
5. **Performance Profiling**: Detailed benchmarking of dimensional verification overhead

## References

- Original DHC-GEP paper: [Add citation]
- SI Base Units: https://www.bipm.org/en/measurement-units
- Prime number encoding: https://en.wikipedia.org/wiki/Prime_number
- Python fractions module: https://docs.python.org/3/library/fractions.html

## Conclusion

These improvements enhance DHC-GEP's dimensional constraint logic by:
- ✓ Eliminating code duplication through centralization
- ✓ Improving performance with caching
- ✓ Documenting full 7-dimension support
- ✓ Providing comprehensive examples and tests
- ✓ Maintaining complete backward compatibility

The system now clearly supports all 7 SI base dimensions and provides better performance for large-scale GEP evolution tasks.
