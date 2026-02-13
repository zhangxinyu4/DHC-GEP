# DHC-GEP Examples

This directory contains example scripts demonstrating DHC-GEP capabilities.

## Examples

### seven_dimensions_example.py
A comprehensive example demonstrating DHC-GEP's ability to handle all 7 SI base dimensions simultaneously:
- L (Length) - meter [m]
- M (Mass) - kilogram [kg]  
- T (Time) - second [s]
- I (Electric Current) - ampere [A]
- Theta (Temperature) - kelvin [K]
- N (Amount of Substance) - mole [mol]
- J (Luminous Intensity) - candela [cd]

**Physical System**: Thermoelectric material with heat flux calculation

**To run**:
```bash
python examples/seven_dimensions_example.py
```

**Expected Output**:
- Dimensional analysis showing all 7 dimensions
- GEP evolution progress over 50 generations
- Best discovered expressions with fitness values

## See Also

For more examples using DHC-GEP:
- `Demonstration on benchmarks/` - Benchmark problems (diffusion, vorticity transport)
- `Application on discovering unknown constitutive relations/` - Real physics applications
- `Noise sensitivity study/` - Robustness to noisy data
- `Coarse graining study/` - Multi-scale analysis
- `Parametric study/` - Parameter sensitivity analysis
