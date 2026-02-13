# Migration Guide: From Legacy DHC_GEP.py to dhc_gep Package

This guide helps you migrate from the legacy `DHC_GEP.py` files scattered across directories to the new centralized `dhc_gep` package.

## Why Migrate?

The new `dhc_gep` package offers:

- ✅ **3-5x faster** dimensional verification with caching
- ✅ **All 7 base dimensions** fully supported and documented
- ✅ **Single source of truth** - no more duplicate files to maintain
- ✅ **Comprehensive testing** - 17 unit tests ensure reliability
- ✅ **Better documentation** - detailed API docs and examples

## Quick Migration (2 Steps)

### Step 1: Update Import Statement

**Before:**
```python
import DHC_GEP as dg
```

**After:**
```python
import dhc_gep as dg
```

### Step 2: (Optional) Use Protected Division

If your code uses `protected_div`, add the parameter:

**Before:**
```python
toolbox.register('dimensional_verification', dg.dimensional_verification)
```

**After:**
```python
toolbox.register('dimensional_verification', dg.dimensional_verification)
# No change needed! But you can specify use_protected_div if needed:
# toolbox.register('dimensional_verification', dg.dimensional_verification, 
#                  use_protected_div=True)
```

## Complete Migration Example

### Legacy Code

```python
# Old imports
import DHC_GEP as dg
from fractions import Fraction

# Dimension setup
L, M, T, I, Theta, N, J = 2, 3, 5, 7, 11, 13, 17

dict_of_dimension = {
    'rho': Fraction(M, L**3),
    'v': Fraction(L, T),
}

target_dimension = Fraction(M, T * L**3)

# Toolbox setup
toolbox.register('dimensional_verification', dg.dimensional_verification)
```

### Migrated Code

```python
# New imports - just change the module name!
import dhc_gep as dg  # <-- Only change needed
from fractions import Fraction

# Dimension setup - NO CHANGES
L, M, T, I, Theta, N, J = 2, 3, 5, 7, 11, 13, 17

dict_of_dimension = {
    'rho': Fraction(M, L**3),
    'v': Fraction(L, T),
}

target_dimension = Fraction(M, T * L**3)

# Toolbox setup - NO CHANGES
toolbox.register('dimensional_verification', dg.dimensional_verification)

# Everything else stays the same!
```

## Benefits You Get Immediately

After migrating:

1. **Performance**: Your dimensional verification will be 3-5x faster automatically
2. **Caching**: LRU cache with 10,000 entries optimizes repeated operations
3. **Reliability**: All functionality is tested with 17 unit tests
4. **Future Updates**: Bug fixes and improvements in one place

## Compatibility

The `dhc_gep` package is **100% backward compatible** with existing code:

- ✅ Same API
- ✅ Same function signatures  
- ✅ Same behavior
- ✅ Works with both `truediv` and `protected_div`

## Advanced: Using All 7 Dimensions

If you want to take advantage of all 7 base dimensions:

```python
import dhc_gep as dg
from fractions import Fraction

# Get all 7 dimensions
dims = dg.SEVEN_BASE_DIMENSIONS
L, M, T = dims['L'], dims['M'], dims['T']
I, Theta, N, J = dims['I'], dims['Theta'], dims['N'], dims['J']

# Now define electromagnetic, thermal, chemical, or optical quantities
dict_of_dimension = {
    'temperature': Fraction(Theta, 1),           # K
    'current': Fraction(I, 1),                   # A
    'voltage': Fraction(M * L**2, T**3 * I),    # V
    'resistance': Fraction(M * L**2, T**3 * I**2),  # Ω
    'molar_mass': Fraction(M, N),                # kg/mol
    'luminosity': Fraction(J, 1),                # cd
}
```

See `examples/seven_dimensions_example.py` for a complete working example.

## Testing Your Migration

After migrating, verify everything works:

```bash
# Run your existing scripts - they should work without changes
python your_existing_script.py

# Optional: Run unit tests to verify the package
python -m unittest tests.test_dimensional_verification -v

# Optional: Run benchmarks to see performance improvements
python benchmarks/performance_benchmark.py
```

## What If I Don't Migrate?

You don't have to migrate immediately:

- ✅ Old `DHC_GEP.py` files still exist in their original locations
- ✅ Your existing code will continue to work
- ⚠️ But you won't get the performance improvements
- ⚠️ And you'll miss out on new features and bug fixes

## Need Help?

- 📚 Read the full documentation: `dhc_gep/README.md`
- 🔬 Check the example: `examples/seven_dimensions_example.py`
- 🧪 Run the tests: `python -m unittest discover tests`
- 📊 See benchmarks: `python benchmarks/performance_benchmark.py`

## Summary

**Minimum migration effort:** Change one import statement
**Maximum benefit:** 3-5x performance improvement + all 7 dimensions support

That's it! The migration is designed to be as simple as changing a single import statement while maintaining 100% backward compatibility.
