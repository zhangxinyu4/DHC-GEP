# DHC-GEP Unit Tests

This directory contains unit tests for DHC-GEP functionality.

## Test Files

### test_dimensional_verification.py
Comprehensive unit tests for the dimensional verification function.

**Test Coverage**:
- Basic L, M, T dimension operations
- Electric current (I) dimension
- Temperature (Theta) dimension  
- Amount of substance (N) dimension
- Luminous intensity (J) dimension
- All 7 dimensions simultaneously
- Addition/subtraction constraints (requires same dimensions)
- Multiplication/division operations
- Dimensionless constants
- Complex nested expressions
- Cache performance

**To run tests**:
```bash
# Using unittest
python -m unittest tests.test_dimensional_verification -v

# Or directly
python tests/test_dimensional_verification.py
```

**Expected Result**: All 11 tests should pass

## Test Results

```
test_cache_improves_performance ... ok
test_addition_same_dimensions ... ok
test_all_seven_dimensions ... ok
test_amount_of_substance_dimension ... ok
test_basic_dimensions_LMT ... ok
test_complex_expression ... ok
test_dimensionless_constant ... ok
test_electric_current_dimension ... ok
test_luminous_intensity_dimension ... ok
test_subtraction_same_dimensions ... ok
test_temperature_dimension ... ok

----------------------------------------------------------------------
Ran 11 tests in 0.004s

OK
```

## Adding New Tests

When adding new dimensional verification tests:
1. Import the `MockIndividual` class or create GEP individuals
2. Define dimension dictionaries using `Fraction` objects
3. Test both valid and invalid expressions
4. Verify dimensional homogeneity is correctly enforced

Example:
```python
def test_new_dimension_combination(self):
    """Test description"""
    dict_of_dimension = {
        'var1': Fraction(M, L**2),
        'var2': Fraction(T)
    }
    target_dimension = Fraction(M, L**2 * T)
    
    valid_ind = MockIndividual("mul(var1,var2)")
    self.assertTrue(
        dg.dimensional_verification(valid_ind, dict_of_dimension, target_dimension)
    )
```
