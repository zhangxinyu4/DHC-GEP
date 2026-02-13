"""
Configuration module for DHC-GEP dimensional analysis.

This module defines the seven base dimensions used in physics:
- L (Length): 2
- M (Mass): 3
- T (Time): 5
- I (Electric Current): 7
- Theta (Temperature): 11
- N (Amount of Substance): 13
- J (Luminous Intensity): 17

Each base dimension is assigned a prime number to enable unique factorization
for dimensional analysis.
"""

# Seven base dimensions with prime number encoding
SEVEN_BASE_DIMENSIONS = {
    'L': 2,      # Length
    'M': 3,      # Mass
    'T': 5,      # Time
    'I': 7,      # Electric Current
    'Theta': 11, # Temperature
    'N': 13,     # Amount of Substance (mole)
    'J': 17      # Luminous Intensity
}


def get_dimension_config():
    """
    Get the seven base dimensions configuration.
    
    Returns:
        dict: Dictionary mapping dimension names to prime numbers.
    """
    return SEVEN_BASE_DIMENSIONS.copy()
