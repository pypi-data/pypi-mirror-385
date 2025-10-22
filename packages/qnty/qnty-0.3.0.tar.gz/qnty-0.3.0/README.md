# Qnty

**High-performance unit system library for Python with dimensional safety and fast unit conversions for engineering calculations.**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Development Status](https://img.shields.io/badge/status-beta-orange.svg)](https://pypi.org/project/qnty/)

## ⚠️ Important Disclaimer

**🚧 Work in Progress**: Qnty is currently in active development and has not been thoroughly vetted for production engineering calculations. While we strive for accuracy, this library should not be used for critical engineering applications without independent verification.

**📐 Accuracy Notice**: The authors are not responsible or liable for incorrect results, calculation errors, or any consequences arising from the use of this library. Always validate calculations independently using established engineering tools and practices.

*Use Qnty to help prevent unit errors, but always verify critical calculations through multiple methods.*

---

## ✨ Key Features

- **🚀 Ultra-Fast Performance**: Prime number encoding and pre-computed conversion tables
- **🛡️ Type Safety**: Compile-time dimensional analysis prevents unit errors
- **⚡ Zero-Cost Abstractions**: Optimized operations with `__slots__` and caching
- **🔗 Fluent API**: Intuitive method chaining for readable code
- **🧮 Engineering-Focused**: Built for real-world engineering calculations
- **🧬 Mathematical System**: Built-in equation solving and expression trees
- **📊 Comprehensive Testing**: 80+ tests with performance benchmarks and real engineering examples

## 🚀 Quick Start

### Installation

```bash
pip install qnty
```

### Basic Usage

```python
from qnty import Length, Pressure, Area

# Create quantities with dimensional safety
width = Length(3, "meter", "Width")
height = Length(2, "meter", "Height")

# Mathematical operations preserve dimensional integrity
area = width * height  # Automatically becomes Area quantity
print(f"Area: {area}")  # Area: 6.0 m²

# Fluent API for unit conversions
print(f"In square feet: {area.to_unit.square_foot}")  # 64.58 ft²
```

### Engineering Example

```python
from qnty import Problem, Length, Pressure, Dimensionless
from qnty.algebra import equation

class PipeDesign(Problem):
    """ASME B31.3 Pipe Wall Thickness Calculation"""

    # Known parameters (fluent API)
    P = Pressure("Design Pressure").set(90).pound_force_per_square_inch
    D = Length("Outside Diameter").set(0.84).inch
    S = Pressure("Allowable Stress").set(20000).pound_force_per_square_inch
    E = Dimensionless("Quality Factor").set(0.8).dimensionless
    Y = Dimensionless("Y Coefficient").set(0.4).dimensionless

    # Unknowns to solve
    t = Length("Pressure Design Thickness")
    P_max = Pressure("Maximum Allowable Pressure")

    # ASME equations
    t_eqn = equation(t, (P * D) / (2 * (S * E + P * Y)))
    P_max_eqn = equation(P_max, (2 * t * S * E) / (D - 2 * t * Y))

# Solve and validate
problem = PipeDesign()
problem.solve()
print(f"Required thickness: {problem.t}")
print(f"Max pressure: {problem.P_max}")
```

### Mathematical Operations

```python
from qnty import Length, Area, Force, Pressure
from qnty.algebra import sqrt

# Mathematical functions preserve dimensional correctness
area = Area(25, "square_meter")
side = sqrt(area)  # Returns Length, not Area!
print(f"Side length: {side}")  # 5.0 m

# Unit conversions with type safety
force = Force(100, "newton")
pressure_area = Area(0.01, "square_meter")
pressure = force / pressure_area  # Automatically becomes Pressure
print(f"Pressure: {pressure.to_unit.pound_force_per_square_inch}")  # 145.04 psi
```

## 📚 Documentation & Examples

- **[🏗️ Examples](examples/)** - Real-world engineering problems including pipe design, composed problems, and conversions
- **[🔧 Development Guide](CLAUDE.md)** - Architecture and development guidelines
- **[📊 Performance Benchmarks](tests/test_benchmark.py)** - Comparison with Pint and other libraries

## 🚀 Performance

Qnty significantly outperforms other unit libraries with **18.9x average speedup** over Pint:

| Operation | Qnty | Pint | **Speedup** |
|-----------|------|------|-------------|
| Mixed Unit Addition | 0.76 μs | 17.52 μs | **23.1x** |
| Complex ASME Equation | 4.07 μs | 106.17 μs | **26.1x** 🚀 |
| Type-Safe Variables | 0.98 μs | 9.65 μs | **9.8x** |
| **AVERAGE** | **1.89 μs** | **35.83 μs** | **18.9x** 🏆 |

*Run `pytest tests/test_benchmark.py -v -s` to verify on your system.*

## 🧮 100+ Engineering Quantities

Qnty provides comprehensive coverage of engineering domains:

```python
from qnty import (
    # Mechanical
    Length, Area, Volume, Mass, Force, Pressure, Temperature,
    # Electrical  
    ElectricPotential, ElectricCurrentIntensity, ElectricResistance,
    # Thermal
    ThermalConductivity, HeatTransferCoefficient,
    # Fluid Dynamics
    ViscosityDynamic, MassFlowRate, VolumetricFlowRate,
    # And 80+ more...
)
```

## 🔧 Development

```bash
# Install for development
pip install -e ".[dev,benchmark]"

# Run all tests (80+ comprehensive tests)
pytest

# Run specific test module
pytest tests/test_dimension.py -v

# Run performance benchmarks vs Pint
pytest tests/test_benchmark.py -v -s

# Code formatting and linting
ruff check src/ tests/
ruff format src/ tests/

# Regenerate auto-generated catalog files
python codegen/cli.py
```

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

We welcome contributions! Please see [CLAUDE.md](CLAUDE.md) for development guidelines and:

1. Fork the repository
2. Create a feature branch
3. Add comprehensive tests for new functionality
4. Ensure all tests pass: `pytest`
5. Verify performance benchmarks: `pytest tests/test_benchmark.py -s`
6. Run code quality checks: `ruff check src/ tests/`
7. Submit a pull request

**Important**: Never edit `*_catalog.py` files directly - they are auto-generated. Modify generators in `codegen/` instead.

---

**Ready to supercharge your engineering calculations?** 🚀

- Explore the **[Examples](examples/)** - Real ASME pipe design, composed problems, and more
- Check the **[Performance Benchmarks](tests/test_benchmark.py)** - See the 18.9x speedup
- Read the **[Development Guide](CLAUDE.md)** - Architecture and contribution guidelines
