# DHC-GEP Tests

This directory contains unit tests for the DHC-GEP package.

## Running Tests

To run all tests:

```bash
python -m unittest discover tests
```

To run a specific test file:

```bash
python -m unittest tests.test_dimensional_verification
```

To run with verbose output:

```bash
python -m unittest tests.test_dimensional_verification -v
```

## Test Coverage

### test_dimensional_verification.py

Tests for the dimensional verification system:

- **TestDimensionalVerification**: Basic dimensional operations and all 7 base dimensions
- **TestPerformanceOptimizations**: Caching mechanisms and performance improvements
- **TestSevenDimensionsConfig**: Configuration of the seven base dimensions

## Test Structure

Each test class focuses on a specific aspect:

1. **Dimensional Operations**: Addition, subtraction, multiplication, division
2. **Seven Dimensions Support**: L, M, T, I, Theta, N, J
3. **Caching**: LRU cache for Fraction operations
4. **Configuration**: Seven dimensions configuration system
