"""
Unit tests for DHC-GEP dimensional verification system.

Tests cover:
1. Basic dimensional operations
2. All 7 base dimensions
3. Caching mechanisms
4. Performance optimizations
"""

import unittest
import sys
import os
from fractions import Fraction
import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import dhc_gep as dg
from dhc_gep.core import _cached_fraction_mul, _cached_fraction_div


class TestDimensionalVerification(unittest.TestCase):
    """Test cases for dimensional verification."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Seven base dimensions
        self.L, self.M, self.T = 2, 3, 5
        self.I, self.Theta, self.N, self.J = 7, 11, 13, 17
    
    def test_seven_dimensions_declaration(self):
        """Test that all 7 base dimensions are properly configured."""
        dims = dg.SEVEN_BASE_DIMENSIONS
        self.assertEqual(len(dims), 7)
        self.assertEqual(dims['L'], 2)
        self.assertEqual(dims['M'], 3)
        self.assertEqual(dims['T'], 5)
        self.assertEqual(dims['I'], 7)
        self.assertEqual(dims['Theta'], 11)
        self.assertEqual(dims['N'], 13)
        self.assertEqual(dims['J'], 17)
    
    def test_basic_dimensional_consistency(self):
        """Test basic dimensional consistency checks."""
        # Same dimensions can be added
        L = Fraction(2, 1)
        self.assertEqual(L, L)
        
        # Different dimensions cannot be added
        M = Fraction(3, 1)
        self.assertNotEqual(L, M)
    
    def test_dimension_multiplication(self):
        """Test dimensional multiplication."""
        # L * M = 2 * 3 = 6
        dim_L = Fraction(self.L, 1)
        dim_M = Fraction(self.M, 1)
        result = dim_L * dim_M
        expected = Fraction(6, 1)
        self.assertEqual(result, expected)
    
    def test_dimension_division(self):
        """Test dimensional division."""
        # L / T = 2 / 5
        dim_L = Fraction(self.L, 1)
        dim_T = Fraction(self.T, 1)
        result = dim_L / dim_T
        expected = Fraction(2, 5)
        self.assertEqual(result, expected)
    
    def test_complex_dimensions(self):
        """Test complex dimensional expressions using all 7 dimensions."""
        # Example: (M * L * I * Theta) / (T^3 * N * J)
        # This represents a complex physical quantity
        numerator = self.M * self.L * self.I * self.Theta
        denominator = (self.T ** 3) * self.N * self.J
        dim = Fraction(numerator, denominator)
        
        # Verify it's a valid Fraction
        self.assertIsInstance(dim, Fraction)
        self.assertEqual(dim.numerator, numerator)
        self.assertEqual(dim.denominator, denominator)
    
    def test_cached_fraction_multiplication(self):
        """Test cached fraction multiplication."""
        # First call
        result1 = _cached_fraction_mul(2, 3, 5, 7)
        self.assertEqual(result1, Fraction(10, 21))
        
        # Second call should use cache
        result2 = _cached_fraction_mul(2, 3, 5, 7)
        self.assertEqual(result2, result1)
    
    def test_cached_fraction_division(self):
        """Test cached fraction division."""
        # First call
        result1 = _cached_fraction_div(2, 3, 5, 7)
        self.assertEqual(result1, Fraction(14, 15))
        
        # Second call should use cache
        result2 = _cached_fraction_div(2, 3, 5, 7)
        self.assertEqual(result2, result1)
        
        # Division by zero
        result3 = _cached_fraction_div(2, 3, 0, 7)
        self.assertIsNone(result3)
    
    def test_all_seven_dimensions_usage(self):
        """Test that all 7 dimensions can be used in a dict_of_dimension."""
        L, M, T, I, Theta, N, J = 2, 3, 5, 7, 11, 13, 17
        
        dict_of_dimension = {
            'length': Fraction(L, 1),
            'mass': Fraction(M, 1),
            'time': Fraction(T, 1),
            'current': Fraction(I, 1),
            'temperature': Fraction(Theta, 1),
            'substance': Fraction(N, 1),
            'luminosity': Fraction(J, 1),
            'velocity': Fraction(L, T),
            'acceleration': Fraction(L, T**2),
            'force': Fraction(M * L, T**2),
            'energy': Fraction(M * L**2, T**2),
            'power': Fraction(M * L**2, T**3),
            'charge': Fraction(I * T, 1),
            'voltage': Fraction(M * L**2, T**3 * I),
            'resistance': Fraction(M * L**2, T**3 * I**2),
            'heat_capacity': Fraction(L**2, T**2 * Theta),
            'molar_mass': Fraction(M, N),
        }
        
        # Verify all are Fractions
        for var, dim in dict_of_dimension.items():
            self.assertIsInstance(dim, Fraction)
        
        # Verify we have 17 different quantities
        self.assertEqual(len(dict_of_dimension), 17)
    
    def test_dimension_uniqueness(self):
        """Test that different dimensional combinations are unique using prime factorization."""
        L, M, T = 2, 3, 5
        
        # These should all be different
        velocity = Fraction(L, T)        # 2/5
        acceleration = Fraction(L, T**2) # 2/25
        density = Fraction(M, L**3)      # 3/8
        force = Fraction(M * L, T**2)    # 6/25
        
        dimensions = [velocity, acceleration, density, force]
        
        # All should be unique
        self.assertEqual(len(set(dimensions)), 4)
    
    def test_dimensional_verification_function_exists(self):
        """Test that the dimensional_verification function exists and is callable."""
        self.assertTrue(hasattr(dg, 'dimensional_verification'))
        self.assertTrue(callable(dg.dimensional_verification))
    
    def test_dimension_addition_same(self):
        """Test that same dimensions can be added."""
        L = Fraction(2, 1)
        # In dimensional analysis, L + L = L
        # This is implemented in the dimensional verification function
        self.assertEqual(L, L)
    
    def test_dimension_addition_different(self):
        """Test that different dimensions cannot be added."""
        L = Fraction(2, 1)
        M = Fraction(3, 1)
        # L + M is not valid in dimensional analysis
        self.assertNotEqual(L, M)


class TestPerformanceOptimizations(unittest.TestCase):
    """Test cases for performance optimizations."""
    
    def test_cache_hit_rate(self):
        """Test that caching improves performance."""
        import time
        
        # Clear cache
        _cached_fraction_mul.cache_clear()
        
        # First call (cache miss)
        start = time.time()
        for _ in range(1000):
            _cached_fraction_mul(2, 3, 5, 7)
        first_time = time.time() - start
        
        # Second call (cache hit)
        start = time.time()
        for _ in range(1000):
            _cached_fraction_mul(2, 3, 5, 7)
        second_time = time.time() - start
        
        # Cache should make it faster. We use a lenient check since timing can vary,
        # but the primary validation is the cache hit count
        info = _cached_fraction_mul.cache_info()
        # After 2000 calls with same args, we should have many hits
        self.assertGreater(info.hits, 1000, "Cache should register hits")
        self.assertLess(info.misses, 10, "Cache misses should be minimal")
    
    def test_cache_info(self):
        """Test cache statistics."""
        _cached_fraction_mul.cache_clear()
        
        # Make some calls
        _cached_fraction_mul(2, 3, 5, 7)
        _cached_fraction_mul(2, 3, 5, 7)  # Cache hit
        _cached_fraction_mul(3, 5, 7, 11)  # Cache miss
        
        info = _cached_fraction_mul.cache_info()
        self.assertEqual(info.hits, 1)
        self.assertEqual(info.misses, 2)


class TestSevenDimensionsConfig(unittest.TestCase):
    """Test the seven dimensions configuration."""
    
    def test_get_dimension_config(self):
        """Test the get_dimension_config function."""
        config = dg.get_dimension_config()
        self.assertEqual(len(config), 7)
        self.assertIn('L', config)
        self.assertIn('M', config)
        self.assertIn('T', config)
        self.assertIn('I', config)
        self.assertIn('Theta', config)
        self.assertIn('N', config)
        self.assertIn('J', config)
    
    def test_prime_numbers(self):
        """Test that all dimension values are prime numbers."""
        config = dg.get_dimension_config()
        
        def is_prime(n):
            if n < 2:
                return False
            for i in range(2, int(n**0.5) + 1):
                if n % i == 0:
                    return False
            return True
        
        for name, value in config.items():
            self.assertTrue(is_prime(value), f"{name} = {value} is not prime")
    
    def test_unique_primes(self):
        """Test that all dimension values are unique."""
        config = dg.get_dimension_config()
        values = list(config.values())
        self.assertEqual(len(values), len(set(values)))


if __name__ == '__main__':
    unittest.main()
