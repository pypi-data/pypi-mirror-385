# CLAUDE.md - Core Module

This document describes the architecture and development patterns for the `qnty.core` module, which provides the fundamental building blocks for the Qnty library's dimensional analysis and unit system.

## Module Overview

The core module implements a strict dependency hierarchy to prevent circular imports:
```
dimension → unit → quantity → quantity_meta → catalogs
```

## Core Files

### Foundation Layer

**`dimension.py` (298 lines)**
- Prime number encoding for dimensional analysis using `PRIMES = (2, 3, 5, 7, 11, 13, 17)`
- `DimBackend` protocol with `PrimeIntBackend` implementation for fast compatibility checks
- Base dimensions: Length(L), Mass(M), Time(T), Current(A), Temperature(Θ), Amount(N), Luminous Intensity(J)
- `Dimension` class with arithmetic operations (`__mul__`, `__truediv__`, `__pow__`)
- Dimension registry with `add_dimension()` and `add_derived()` functions

**`unit.py` (613 lines)**
- Unit registry with pre-computed conversion tables via `si_factor`
- SI prefix system (`allow_prefix=True`, `expose_prefixed_to_u=True`)
- `Unit` class with dimension compatibility and conversion methods
- `UnitNamespace` for grouped access to related units
- Unit normalization with aggressive string cleaning (`_norm()`)
- Global unit registry `ureg` and shorthand `u` namespace

### Quantity System

**`quantity.py` (503 lines)**
- Unified `Quantity` class combining concrete values and named placeholders
- Generic type parameter `D` for dimension safety
- Fluent setter API: `quantity.set(100).unit_name`
- Unit conversion: `quantity.to_unit.inches` and `quantity.as_unit.inches`
- Auto-detection of variable names for equation solving symbols
- Mathematical operations return expressions from algebra module

**`quantity_meta.py` (167 lines)**
- Metaclass system for automatic quantity class generation
- `@quantity(UnitNamespace)` decorator pattern
- Dynamic binding of unit namespace methods to quantity classes
- Creates `QuantitySetter`, `UnitApplier`, and `UnitChanger` helper classes

### Generated Catalogs

**`dimension_catalog.py` (32 lines)** - ⚠️ Generated File
- Pre-defined dimensional constants accessible via `dim.L`, `dim.Force`, etc.
- Common derived dimensions: Force, Area, Volume, Pressure, Energy, Power
- Generated from `codegen/generators/` - do not edit directly

**`unit_catalog.py` (220 lines)** - ⚠️ Generated File
- Unit definitions with SI factors and aliases
- Unit namespace classes (e.g., `LengthUnits`, `PressureUnits`)
- Generated from `codegen/generators/` - do not edit directly

**`quantity_catalog.py` (19 lines)** - ⚠️ Generated File
- Quantity classes using `@quantity` decorator pattern
- Examples: `Acceleration`, `Length`, `Dimensionless`
- Generated from `codegen/generators/` - do not edit directly

### Module Interface

**`__init__.py` (17 lines)**
- Exports key symbols: `dim`, `u`, `Q`, and all quantity classes
- Clean public API hiding internal implementation details

## Key Development Patterns

### Dimension Safety
```python
# Dimensions are encoded using prime numbers for fast operations
L = add_dimension((1,0,0,0,0,0,0))  # Length
M = add_dimension((0,1,0,0,0,0,0))  # Mass
Force = add_derived(M * L / (T**2))  # Derived dimension
```

### Unit Registration
```python
meter = add_unit(
    dim.L, symbol="m", si_factor=1.0,
    aliases=("meters", "metre", "metres"),
    allow_prefix=True, expose_prefixed_to_u=True
)
```

### Quantity Creation
```python
@quantity(uc.LengthUnits)
class Length:
    """Length quantity with automatic boilerplate."""
    pass
```

### Performance Optimizations
- `__slots__` used throughout for memory efficiency
- Pre-computed conversion tables via `si_factor`
- Prime number encoding for O(1) dimensional compatibility checks
- Cached dimension signatures and SI factors

## Import Guidelines

Due to the strict dependency hierarchy:
- Use `TYPE_CHECKING` guards for type-only imports
- Never import from higher-level modules (algebra, problems, solving)
- Import order: dimension → unit → quantity → quantity_meta → catalogs

## Code Generation

Three files are auto-generated and should not be edited directly:
- `dimension_catalog.py`
- `unit_catalog.py`
- `quantity_catalog.py`

To modify behavior in these files, update the generators in `codegen/generators/` and run:
```bash
python codegen/cli.py
```

## Testing Commands

```bash
pytest tests/test_dimension.py -v    # Test dimensional analysis
pytest tests/test_unit.py -v        # Test unit system
pytest tests/test_quantity.py -v    # Test quantity operations
```