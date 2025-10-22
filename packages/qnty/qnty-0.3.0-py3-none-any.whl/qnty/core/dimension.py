# dimensions_core.py - Optimized version with caching and improved algorithms
from __future__ import annotations

import functools
import inspect
import re
from collections.abc import Iterable
from dataclasses import dataclass
from types import MappingProxyType
from typing import Final, Protocol

# =======================
# Configuration
# =======================
N_BASE: Final[int] = 7  # number of base axes (e.g., L,M,T,I,Θ,N,J)

# =======================
# Prime-int backend (num/den)
# =======================
DimVec = tuple[int, ...]
PRIMES: Final[tuple[int, ...]] = (2, 3, 5, 7, 11, 13, 17)  # extend if >10 bases


def vadd(a: DimVec, b: DimVec) -> DimVec:
    return tuple(a[i] + b[i] for i in range(len(a)))


def vsub(a: DimVec, b: DimVec) -> DimVec:
    return tuple(a[i] - b[i] for i in range(len(a)))


def vpow(a: DimVec, k: int) -> DimVec:
    if k == 0:
        return (0,) * len(a)
    if k == 1:
        return a
    if k == -1:
        return tuple(-x for x in a)
    return tuple(x * k for x in a)


def zeros(n: int = N_BASE) -> DimVec:
    return (0,) * n


class DimBackend(Protocol):
    def encode(self, v: DimVec) -> tuple[int, ...]: ...
    def mul(self, a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]: ...
    def div(self, a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]: ...
    def pow(self, a: tuple[int, ...], k: int) -> tuple[int, ...]: ...


# Cached GCD function
@functools.lru_cache(maxsize=256)
def _cached_gcd(a: int, b: int) -> int:
    """Cached GCD computation using binary algorithm."""
    if a == 0:
        return b
    if b == 0:
        return a

    # Binary GCD algorithm (faster than Euclidean for integers)
    shift = 0
    while ((a | b) & 1) == 0:
        a >>= 1
        b >>= 1
        shift += 1

    while (a & 1) == 0:
        a >>= 1

    while b != 0:
        while (b & 1) == 0:
            b >>= 1
        if a > b:
            a, b = b, a
        b -= a

    return a << shift


class PrimeIntBackend:
    """Compact prime code: (num:int, den:int) with GCD reduction and caching."""

    __slots__ = ("_reduce_cache",)

    def __init__(self):
        self._reduce_cache = {}

    def encode(self, v: DimVec) -> tuple[int, ...]:
        # Fast path for common cases
        if not any(v):  # All zeros
            return (1, 1)

        num = den = 1

        # Unrolled loop for better performance
        for i, e in enumerate(v):
            if e == 0:
                continue
            p = PRIMES[i]
            if e > 0:
                num *= p**e
            else:
                den *= p ** (-e)

        return self._reduce(num, den)

    def mul(self, a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
        return self._reduce(a[0] * b[0], a[1] * b[1])

    def div(self, a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
        return self._reduce(a[0] * b[1], a[1] * b[0])

    def pow(self, a: tuple[int, ...], k: int) -> tuple[int, ...]:
        if k == 0:
            return (1, 1)
        if k == 1:
            return a
        if k == -1:
            return (a[1], a[0])

        if k > 0:
            # Use fast exponentiation for large powers
            if k > 3:
                num = self._fast_pow(a[0], k)
                den = self._fast_pow(a[1], k)
            else:
                num = a[0] ** k
                den = a[1] ** k
            return self._reduce(num, den)
        else:
            k = -k
            if k > 3:
                num = self._fast_pow(a[1], k)
                den = self._fast_pow(a[0], k)
            else:
                num = a[1] ** k
                den = a[0] ** k
            return self._reduce(num, den)

    @staticmethod
    def _fast_pow(base: int, exp: int) -> int:
        """Fast integer exponentiation using binary method."""
        if exp == 0:
            return 1
        if exp == 1:
            return base
        if exp == 2:
            return base * base

        result = 1
        while exp > 0:
            if exp & 1:
                result *= base
            base *= base
            exp >>= 1
        return result

    def _reduce(self, num: int, den: int) -> tuple[int, ...]:
        """Reduce fraction to lowest terms with caching."""
        # Handle negative denominators
        if den < 0:
            num, den = -num, -den

        # Fast paths
        if den == 1 or num == 0:
            return (num, 1 if den != 0 else 0)
        if num == den:
            return (1, 1)

        # Check cache
        cache_key = (num, den)
        if cache_key in self._reduce_cache:
            return self._reduce_cache[cache_key]

        # Compute GCD
        g = _cached_gcd(abs(num), den)
        if g > 1:
            num //= g
            den //= g

        result = (num, den)

        # Cache result (limit cache size)
        if len(self._reduce_cache) < 1024:
            self._reduce_cache[cache_key] = result

        return result


# --- Tuple backend (direct exponent vectors) ---
class TupleBackend:
    """Direct exponent vectors with optimizations."""

    __slots__ = ()

    def encode(self, v: DimVec) -> DimVec:
        return v

    def mul(self, a: DimVec, b: DimVec) -> DimVec:
        return tuple(a[i] + b[i] for i in range(len(a)))

    def div(self, a: DimVec, b: DimVec) -> DimVec:
        return tuple(a[i] - b[i] for i in range(len(a)))

    def pow(self, a: DimVec, k: int) -> DimVec:
        if k == 0:
            return (0,) * len(a)
        if k == 1:
            return a
        if k == -1:
            return tuple(-x for x in a)
        return tuple(x * k for x in a)


# Use optimized PrimeIntBackend by default
BACKEND: DimBackend = PrimeIntBackend()
# BACKEND: DimBackend = TupleBackend()


# =======================
# Dimension (frozen) with caching
# =======================
@dataclass(frozen=True, slots=True)
class Dimension:
    exps: DimVec  # canonical tuple (immutable)
    code: tuple[int, ...]  # compact prime code (immutable ints)

    def __mul__(self, o: Dimension) -> Dimension:
        # Check cache first
        cache_key = (self.code, o.code)
        if hasattr(Dimension, "_mul_cache") and cache_key in Dimension._mul_cache:
            return Dimension._mul_cache[cache_key]

        result = Dimension(vadd(self.exps, o.exps), BACKEND.mul(self.code, o.code))

        # Cache result (limit cache size)
        if not hasattr(Dimension, "_mul_cache"):
            Dimension._mul_cache = {}
        if len(Dimension._mul_cache) < 256:
            Dimension._mul_cache[cache_key] = result

        return result

    def __truediv__(self, o: Dimension) -> Dimension:
        # Check cache first
        cache_key = (self.code, o.code)
        if hasattr(Dimension, "_div_cache") and cache_key in Dimension._div_cache:
            return Dimension._div_cache[cache_key]

        result = Dimension(vsub(self.exps, o.exps), BACKEND.div(self.code, o.code))

        # Cache result (limit cache size)
        if not hasattr(Dimension, "_div_cache"):
            Dimension._div_cache = {}
        if len(Dimension._div_cache) < 256:
            Dimension._div_cache[cache_key] = result

        return result

    def __pow__(self, k: int) -> Dimension:
        # Fast paths
        if k == 0:
            return _DIMENSIONLESS
        if k == 1:
            return self

        # Check cache
        cache_key = (self.code, k)
        if hasattr(Dimension, "_pow_cache") and cache_key in Dimension._pow_cache:
            return Dimension._pow_cache[cache_key]

        result = Dimension(vpow(self.exps, k), BACKEND.pow(self.code, k))

        # Cache result (limit cache size)
        if not hasattr(Dimension, "_pow_cache"):
            Dimension._pow_cache = {}
        if len(Dimension._pow_cache) < 256:
            Dimension._pow_cache[cache_key] = result

        return result

    def __eq__(self, o: object) -> bool:
        return isinstance(o, Dimension) and self.code == o.code

    def __hash__(self) -> int:
        return hash(self.code)

    def __repr__(self) -> str:
        if isinstance(self.code, tuple) and len(self.code) == 2:
            num, den = self.code
            return f"Dim{self.exps} [{num}/{den}]"
        else:
            return f"Dim{self.exps} {self.code}"

    # --- handy predicates ---
    def is_dimensionless(self) -> bool:
        # Fast check for prime backend
        if isinstance(self.code, tuple) and len(self.code) == 2:
            return self.code == (1, 1)
        # Fallback for tuple backend
        return all(e == 0 for e in self.exps)

    def is_angle(self) -> bool:
        # If you treat radians as a distinct base (Theta index)
        return self.exps == (0, 0, 0, 0, 1, 0, 0)


# Initialize class-level caches for Dimension
Dimension._mul_cache = {}  # type: ignore[attr-defined]
Dimension._div_cache = {}  # type: ignore[attr-defined]
Dimension._pow_cache = {}  # type: ignore[attr-defined]

# Pre-create dimensionless constant
_DIMENSIONLESS = Dimension(zeros(), BACKEND.encode(zeros()))


# =======================
# Global namespace (sealed) + registry + helpers
# =======================
class Dimensions:
    __slots__ = ("__sealed", "__dict__")

    def __init__(self):
        object.__setattr__(self, "_Dimensions__sealed", False)

    def __setattr__(self, k, v):
        if self.__sealed:
            raise AttributeError("dim is sealed; cannot modify.")
        object.__setattr__(self, k, v)


# =======================
# Optional: declarative catalog metaclass (frozen)
# =======================
class DimensionNamespaceMeta(type):
    """
    Declarative catalogs:
      - Any class attr that is a tuple[int,...] becomes a Dimension (base)
      - Any class attr that is a callable(cls)->Dimension is evaluated as derived
      - All Dimensions are auto-registered on global `dim` (frozen)
    """

    def __new__(mcls, name, bases, ns):
        cls = super().__new__(mcls, name, bases, ns)
        # 1) base tuples -> Dimension
        for k, v in list(ns.items()):
            if isinstance(v, tuple) and all(isinstance(x, int) for x in v):
                d = Dimension(v, BACKEND.encode(v))
                setattr(cls, k, d)
        # 2) callables(cls) -> derived Dimensions
        for k, v in list(ns.items()):
            if callable(v):
                d = v(cls)
                if not isinstance(d, Dimension):
                    raise TypeError(f"{name}.{k} did not return a Dimension")
                setattr(cls, k, d)
        # 3) register to global dim
        for k, v in cls.__dict__.items():
            # Skip special attributes (like __slots__, __module__, etc.)
            if k.startswith("__") and k.endswith("__"):
                continue
            if isinstance(v, Dimension):
                if k in _dim_registry or k in _dim_aliases:
                    raise KeyError(f"Dimension '{k}' already defined.")
                setattr(dim, k, v)
                _dim_registry[k] = v

        # freeze class
        def _blocked_setattr(self, *_a, **_k):  # type: ignore[unused-argument]
            raise AttributeError(f"{name} is frozen; define dimensions in the class body.")

        cls.__setattr__ = _blocked_setattr  # type: ignore[attr-defined]
        return cls


class DimensionNamespace(metaclass=DimensionNamespaceMeta):
    __slots__ = ()


dim = Dimensions()

# registries
_dim_registry: dict[str, Dimension] = {}  # canonical names -> Dimension
_dim_aliases: dict[str, str] = {}  # alias -> canonical name


def _caller_var_name(fn: str) -> str:
    """Best-effort LHS variable name from the calling source line."""
    frame = inspect.currentframe()
    if frame is None or frame.f_back is None or frame.f_back.f_back is None:
        raise RuntimeError("Could not access call stack for variable name detection")
    frame = frame.f_back.f_back
    frame_info = inspect.getframeinfo(frame)
    if frame_info.code_context is None or not frame_info.code_context:
        raise RuntimeError("Could not get source code context for variable name detection")
    line = frame_info.code_context[0]
    # Support Unicode identifiers (like Θ) in addition to ASCII
    m = re.match(rf"\s*([\w_][\w\d_]*)\s*=\s*{fn}\b", line, re.UNICODE)
    if not m:
        raise RuntimeError("Could not auto-detect variable name for registration")
    return m.group(1)


def add_dimension(exps: DimVec, *, name: str | None = None, aliases: Iterable[str] = ()) -> Dimension:
    """Create a base Dimension from raw exponents, register on `dim`, support aliases."""
    if name is None:
        name = _caller_var_name("add_dimension")
    if name in _dim_registry or name in _dim_aliases:
        raise KeyError(f"Dimension name '{name}' already defined.")
    v = tuple(exps)
    d = Dimension(v, BACKEND.encode(v))
    setattr(dim, name, d)
    _dim_registry[name] = d
    for a in aliases:
        if a in _dim_registry or a in _dim_aliases:
            raise KeyError(f"Dimension alias '{a}' already in use.")
        setattr(dim, a, d)
        _dim_aliases[a] = name
    return d


def add_derived(d: Dimension, *, name: str | None = None, aliases: Iterable[str] = ()) -> Dimension:
    """Register an already-composed Dimension (using *, /, **)."""
    if name is None:
        name = _caller_var_name("add_derived")
    if name in _dim_registry or name in _dim_aliases:
        raise KeyError(f"Dimension name '{name}' already defined.")
    setattr(dim, name, d)
    _dim_registry[name] = d
    for a in aliases:
        if a in _dim_registry or a in _dim_aliases:
            raise KeyError(f"Dimension alias '{a}' already in use.")
        setattr(dim, a, d)
        _dim_aliases[a] = name
    return d


def seal_dimensions() -> None:
    """Freeze the dim namespace to prevent accidental modification."""
    object.__setattr__(dim, "_Dimensions__sealed", True)


def dimensions_map() -> MappingProxyType[str, Dimension]:
    """Immutable view of canonical dimension registry (excludes aliases)."""
    return MappingProxyType(_dim_registry)


def write_dimensions_stub(path: str = "dimensions.pyi") -> None:
    """Generate a .pyi stub so tools know all dim.<name> and alias attributes."""
    with open(path, "w", encoding="utf-8") as f:
        f.write("from typing import Final\n")
        f.write("\n")
        f.write("from .core import Dimension\n\n")
        f.write("class Dimensions:\n")
        for name in sorted(_dim_registry):
            f.write(f"    {name}: Final[Dimension]\n")
        for alias, canonical in sorted(_dim_aliases.items()):
            f.write(f"    {alias}: Final[Dimension]  # alias for {canonical}\n")
        f.write("\n")
        f.write("dim: Final[Dimensions]\n")


# Seal once finished defining everything in this module
def seal_dimensions_now() -> None:
    # Call this from your package __init__ after all catalogs/defs are loaded.
    seal_dimensions()


# =======================
# Example declarative catalog (optional)
# =======================
# class MechanicsDims(DimensionNamespace):
#     # You can re-declare for namespacing or add field-specific ones.
#     # Base (tuples):
#     L = (1,0,0,0,0,0,0)
#     M = (0,1,0,0,0,0,0)
#     T = (0,0,1,0,0,0,0)
#     # Explicit dimensionless in the catalog too (optional):
#     Dimensionless = zeros()

#     # Derived (callables receive the class with bound Dimensions):
#     Area     = lambda cls: cls.L * cls.L
#     Volume   = lambda cls: cls.L ** 3
#     Velocity = lambda cls: cls.L / cls.T
#     Accel    = lambda cls: cls.L / (cls.T ** 2)
#     Force    = lambda cls: cls.M * cls.L / (cls.T ** 2)
#     Pressure = lambda cls: cls.Force / cls.Area
