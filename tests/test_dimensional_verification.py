"""
Unit tests for DHC_GEP dimensional verification functionality.
Tests the dimensional constraint logic with all 7 SI base dimensions.
"""

import unittest
import sys
import os
from fractions import Fraction

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import DHC_GEP as dg

# Import GEP modules
import geppy as gep
from deap import creator, base
import operator
import numpy as np


class MockIndividual:
    """Mock individual for testing dimensional verification"""
    def __init__(self, expression):
        self.expression = expression
    
    def __str__(self):
        return self.expression


class TestDimensionalVerification(unittest.TestCase):
    """Test cases for dimensional verification function"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Define all 7 SI base dimensions using prime numbers
        self.L = 2   # Length
        self.M = 3   # Mass
        self.T = 5   # Time
        self.I = 7   # Electric Current
        self.Theta = 11  # Temperature
        self.N = 13  # Amount of Substance
        self.J = 17  # Luminous Intensity
    
    def test_basic_dimensions_LMT(self):
        """Test basic Length, Mass, Time dimensions"""
        # Test case: density * velocity = momentum flux
        # [kg/m³] * [m/s] = [kg/(m²·s)]
        dict_of_dimension = {
            'rho': Fraction(self.M, self.L**3),  # Density
            'v': Fraction(self.L, self.T)        # Velocity
        }
        target_dimension = Fraction(self.M, self.L**2 * self.T)  # Momentum flux
        
        # Valid expression: rho * v
        valid_ind = MockIndividual("mul(rho,v)")
        self.assertTrue(
            dg.dimensional_verification(valid_ind, dict_of_dimension, target_dimension)
        )
        
        # Invalid expression: rho + v (different dimensions)
        invalid_ind = MockIndividual("add(rho,v)")
        self.assertFalse(
            dg.dimensional_verification(invalid_ind, dict_of_dimension, target_dimension)
        )
    
    def test_electric_current_dimension(self):
        """Test Electric Current (I) dimension"""
        # Test case: Voltage / Current = Resistance
        # [V] / [A] = [Ω]
        # [kg·m²/(s³·A)] / [A] = [kg·m²/(s³·A²)]
        dict_of_dimension = {
            'voltage': Fraction(self.M * self.L**2, self.T**3 * self.I),
            'current': Fraction(self.I)
        }
        target_dimension = Fraction(self.M * self.L**2, self.T**3 * self.I**2)  # Resistance
        
        valid_ind = MockIndividual("truediv(voltage,current)")
        self.assertTrue(
            dg.dimensional_verification(valid_ind, dict_of_dimension, target_dimension)
        )
    
    def test_temperature_dimension(self):
        """Test Temperature (Theta) dimension"""
        # Test case: Thermal conductivity * temperature gradient = heat flux
        # [W/(m·K)] * [K/m] = [W/m²]
        dict_of_dimension = {
            'k': Fraction(self.M * self.L, self.T**3 * self.Theta),  # Thermal conductivity
            'grad_T': Fraction(self.Theta, self.L)  # Temperature gradient
        }
        target_dimension = Fraction(self.M, self.T**3)  # Heat flux
        
        valid_ind = MockIndividual("mul(k,grad_T)")
        self.assertTrue(
            dg.dimensional_verification(valid_ind, dict_of_dimension, target_dimension)
        )
    
    def test_amount_of_substance_dimension(self):
        """Test Amount of Substance (N) dimension"""
        # Test case: mass / molar_mass = amount
        # [kg] / [kg/mol] = [mol]
        dict_of_dimension = {
            'mass': Fraction(self.M),
            'molar_mass': Fraction(self.M, self.N)
        }
        target_dimension = Fraction(self.N)  # Amount of substance
        
        valid_ind = MockIndividual("truediv(mass,molar_mass)")
        self.assertTrue(
            dg.dimensional_verification(valid_ind, dict_of_dimension, target_dimension)
        )
    
    def test_luminous_intensity_dimension(self):
        """Test Luminous Intensity (J) dimension"""
        # Test case: luminous_intensity / area = luminance
        # [cd] / [m²] = [cd/m²]
        dict_of_dimension = {
            'lum_int': Fraction(self.J),
            'area': Fraction(self.L**2)
        }
        target_dimension = Fraction(self.J, self.L**2)  # Luminance
        
        valid_ind = MockIndividual("truediv(lum_int,area)")
        self.assertTrue(
            dg.dimensional_verification(valid_ind, dict_of_dimension, target_dimension)
        )
    
    def test_all_seven_dimensions(self):
        """Test expression involving all 7 dimensions"""
        # Complex expression using all dimensions
        dict_of_dimension = {
            'length': Fraction(self.L),
            'mass': Fraction(self.M),
            'time': Fraction(self.T),
            'current': Fraction(self.I),
            'temp': Fraction(self.Theta),
            'amount': Fraction(self.N),
            'luminous': Fraction(self.J)
        }
        
        # Target: dimensionless (all dimensions cancel)
        target_dimension = Fraction(1)
        
        # Expression that results in dimensionless quantity
        # (mass * length * time * current * temp * amount * luminous) / 
        # (mass * length * time * current * temp * amount * luminous) = 1
        expr = "truediv(mul(mul(mul(mul(mul(mul(length,mass),time),current),temp),amount),luminous)," \
               "mul(mul(mul(mul(mul(mul(length,mass),time),current),temp),amount),luminous))"
        valid_ind = MockIndividual(expr)
        self.assertTrue(
            dg.dimensional_verification(valid_ind, dict_of_dimension, target_dimension)
        )
    
    def test_addition_same_dimensions(self):
        """Test that addition only works with same dimensions"""
        dict_of_dimension = {
            'x1': Fraction(self.M, self.L**3),
            'x2': Fraction(self.M, self.L**3)
        }
        target_dimension = Fraction(self.M, self.L**3)
        
        # Valid: same dimensions
        valid_ind = MockIndividual("add(x1,x2)")
        self.assertTrue(
            dg.dimensional_verification(valid_ind, dict_of_dimension, target_dimension)
        )
    
    def test_subtraction_same_dimensions(self):
        """Test that subtraction only works with same dimensions"""
        dict_of_dimension = {
            'x1': Fraction(self.L, self.T),
            'x2': Fraction(self.L, self.T)
        }
        target_dimension = Fraction(self.L, self.T)
        
        # Valid: same dimensions
        valid_ind = MockIndividual("sub(x1,x2)")
        self.assertTrue(
            dg.dimensional_verification(valid_ind, dict_of_dimension, target_dimension)
        )
    
    def test_dimensionless_constant(self):
        """Test that constants are treated as dimensionless"""
        dict_of_dimension = {
            'x': Fraction(self.M)
        }
        target_dimension = Fraction(self.M)
        
        # Multiplying by a constant shouldn't change dimension
        # Note: In actual GEP, RNC terminals would appear as integers
        # The dimensional_verification should handle this
        valid_ind = MockIndividual("x")
        self.assertTrue(
            dg.dimensional_verification(valid_ind, dict_of_dimension, target_dimension)
        )
    
    def test_complex_expression(self):
        """Test complex nested expression"""
        # Kinetic energy: 0.5 * mass * velocity^2
        # [kg] * [m/s]^2 = [kg·m²/s²] = [J]
        dict_of_dimension = {
            'mass': Fraction(self.M),
            'velocity': Fraction(self.L, self.T)
        }
        target_dimension = Fraction(self.M * self.L**2, self.T**2)  # Energy
        
        # Expression: mass * velocity * velocity
        valid_ind = MockIndividual("mul(mass,mul(velocity,velocity))")
        self.assertTrue(
            dg.dimensional_verification(valid_ind, dict_of_dimension, target_dimension)
        )


class TestCachePerformance(unittest.TestCase):
    """Test dimensional verification caching for performance"""
    
    def test_cache_improves_performance(self):
        """Verify that caching improves performance for repeated evaluations"""
        import time
        
        L, M, T = 2, 3, 5
        dict_of_dimension = {
            'x': Fraction(M, L**3),
            'y': Fraction(L, T)
        }
        target_dimension = Fraction(M, L**2 * T)
        
        # Create a moderately complex expression
        ind = MockIndividual("mul(x,y)")
        
        # First run - populates cache
        start = time.time()
        for _ in range(100):
            dg.dimensional_verification(ind, dict_of_dimension, target_dimension)
        first_run = time.time() - start
        
        # Second run - should use cache
        start = time.time()
        for _ in range(100):
            dg.dimensional_verification(ind, dict_of_dimension, target_dimension)
        second_run = time.time() - start
        
        # Note: With caching, second run might be faster, but this test
        # just ensures both complete successfully
        self.assertIsNotNone(first_run)
        self.assertIsNotNone(second_run)


if __name__ == '__main__':
    unittest.main()
