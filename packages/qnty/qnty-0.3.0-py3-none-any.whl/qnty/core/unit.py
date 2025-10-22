# units_core.py
from __future__ import annotations

import functools
import inspect
import re
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Final, Generic, SupportsIndex, TypeVar

from .dimension import Dimension

# =======================
# Utilities
# =======================
_NORM_DELETE_MAP = str.maketrans(
    {
        " ": None,
        "_": None,
        "-": None,
        "^": None,
        # NOTE: Do NOT remove '·' (middle dot) - it distinguishes N·m (newton-meter) from nm (nanometer)
    }
)


def _norm(s: str) -> str:
    """
    Aggressive normalization used for name/alias keys:
    - casefold
    - remove spaces, underscores, dashes, carets, middle dot
    Optimized with translate to reduce function calls.
    """
    return s.strip().casefold().translate(_NORM_DELETE_MAP)


# Cached version for performance-critical paths
@functools.lru_cache(maxsize=512)
def _norm_cached(s: str) -> str:
    """Cached version of _norm for performance optimization."""
    return _norm(s)


_SUP: Final[dict[int, str]] = {2: "²", 3: "³"}


def _caller_var_name(fn: str) -> str:
    """
    Inspect the caller's line to infer a variable name when `name` is omitted.
    Example expected pattern:  my_unit = add_unit(...)
    """
    frame = inspect.currentframe()
    if frame is None or frame.f_back is None or frame.f_back.f_back is None:
        raise RuntimeError("Could not access call stack for variable name detection")
    frame = frame.f_back.f_back
    frame_info = inspect.getframeinfo(frame)
    if frame_info.code_context is None or not frame_info.code_context:
        raise RuntimeError("Could not get source code context for variable name detection")
    line = frame_info.code_context[0]
    m = re.match(rf"\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*{fn}\b", line)
    if not m:
        raise RuntimeError("Could not auto-detect variable name")
    return m.group(1)


# =======================
# Prefix catalog (SI core)
# =======================
# name, symbol, factor
PREFIXES: Final[tuple[tuple[str, str, float], ...]] = (
    ("kilo", "k", 1e3),
    ("hecto", "h", 1e2),
    ("deca", "da", 1e1),
    ("deci", "d", 1e-1),
    ("centi", "c", 1e-2),
    ("milli", "m", 1e-3),
    ("micro", "μ", 1e-6),  # use 'μ' (mu); we add 'u' ASCII alias on registration
    ("nano", "n", 1e-9),
)

D = TypeVar("D")


# =======================
# Unit (frozen) + operator interning hooks
# =======================
@dataclass(frozen=True, slots=True)
class Unit(Generic[D]):
    name: str
    symbol: str
    dim: Dimension
    si_factor: float
    si_offset: float = 0.0  # reserved for affine scales (e.g., Celsius)
    aliases: tuple[str, ...] = ()

    # --- operator overloads, visible to Pylance ---
    def __mul__(self, other: Unit) -> Unit:
        return _compose(self, other, div=False)

    def __truediv__(self, other: Unit) -> Unit:
        return _compose(self, other, div=True)

    def __pow__(self, k: SupportsIndex) -> Unit:
        return _pow_unit(self, int(k))

    # (optional, harmless)
    def __rmul__(self, other: Unit) -> Unit:
        return _compose(other, self, div=False)

    def __rtruediv__(self, other: Unit) -> Unit:
        return _compose(other, self, div=True)


# --------------------------
# Unit Registry
# --------------------------
class UnitRegistry:
    """
    Registers Units, resolves by name/alias, tracks preferred units by dimension,
    supports interning by symbol (first-wins), and exposes dynamic attribute access
    for ergonomics (ureg.mps2).
    """

    __slots__ = (
        "_by_name",  # normalized name/alias -> Unit
        "_by_symbol",  # symbol -> Unit (last-wins, useful for tooling)
        "_intern_by_symbol",  # symbol -> Unit (first-wins, for interning)
        "_by_dim",  # dim -> {normalized name/alias -> Unit}
        "_preferred",  # dim -> Unit
        "_attr_exposed",  # names/aliases exposed via __getattr__/__dir__
        "_sealed",  # registry sealed flag
        "_resolve_cache",  # cache for resolve() method (performance optimization)
    )

    def __init__(self) -> None:
        self._by_name: dict[str, Unit] = {}
        self._by_symbol: dict[str, Unit] = {}
        self._intern_by_symbol: dict[str, Unit] = {}
        self._by_dim: dict[Dimension, dict[str, Unit]] = {}
        self._preferred: dict[Dimension, Unit] = {}
        self._attr_exposed: dict[str, Unit] = {}
        self._sealed: bool = False
        self._resolve_cache: dict[tuple[str, Dimension | None], Unit | None] = {}

    # ----- sealing -----
    @property
    def sealed(self) -> bool:
        return self._sealed

    def seal(self) -> None:
        self._sealed = True

    # ----- registration -----
    def register(
        self,
        unit: Unit,
        *aliases: str,
        expose_attr: bool = True,
        prefer: bool = False,
    ) -> Unit:
        """
        Register a Unit and optional name aliases.
        - Ensures all keys point to this unit (no cross-unit key reuse).
        - Interns by symbol (first registration wins); keeps a last-wins symbol map too.
        - Optionally exposes names/aliases as ureg.<name> attributes.
        - Optionally marks as preferred for its dimension.
        """
        if self._sealed:
            raise AttributeError("Unit registry is sealed; cannot register.")

        keys = {unit.name, *unit.aliases, *aliases}
        for k in keys:
            nk = _norm(k)
            existing = self._by_name.get(nk)
            if existing is not None and existing is not unit:
                raise ValueError(f"Duplicate unit key '{k}' already registered for {existing.name}")
            self._by_name[nk] = unit

            # dimension index
            self._by_dim.setdefault(unit.dim, {})[nk] = unit

            # expose attribute (skip raw symbol—often non-identifier)
            if expose_attr and k != unit.symbol:
                self._attr_exposed[nk] = unit

        # symbol maps
        self._intern_by_symbol.setdefault(unit.symbol, unit)  # first-wins
        self._by_symbol[unit.symbol] = unit  # last-wins

        if prefer:
            self._preferred[unit.dim] = unit

        # Registrations can invalidate prior negative cache entries.
        self._resolve_cache.clear()

        return unit

    def define(
        self,
        name: str,
        *,
        symbol: str,
        dim: Dimension,
        si_factor: float,
        si_offset: float = 0.0,
        aliases: Iterable[str] = (),
        expose_attr: bool = True,
        prefer: bool = False,
    ) -> Unit:
        """
        Convenience: create a Unit then register it.
        """
        u = Unit(
            name=_norm(name),
            symbol=symbol,
            dim=dim,
            si_factor=float(si_factor),
            si_offset=float(si_offset),
            aliases=tuple(_norm(a) for a in aliases),
        )
        return self.register(u, expose_attr=expose_attr, prefer=prefer)

    # ----- lookup / resolution -----
    def resolve(self, name_or_symbol: str, *, dim: Dimension | None = None) -> Unit | None:
        """
        Resolve by symbol first (fast path), then by normalized name/alias.
        If `dim` is provided, only return a unit that matches that dimension.
        """
        # Check cache first for performance
        cache_key = (name_or_symbol, dim)
        cached_result = self._resolve_cache.get(cache_key)
        if cached_result is not None:
            return cached_result

        # Handle None result in cache (cache misses too)
        if cache_key in self._resolve_cache:
            return None

        # Fast path: try symbols (avoid normalization)
        u = self._intern_by_symbol.get(name_or_symbol)
        if u is None:
            u = self._by_symbol.get(name_or_symbol)
        if u is not None:
            if dim is None or u.dim == dim:
                self._resolve_cache[cache_key] = u
                return u
            self._resolve_cache[cache_key] = None
            return None

        # Fallback: normalized name/alias lookup (use cached version)
        nk = _norm_cached(name_or_symbol)
        u = self._by_name.get(nk)
        if u is not None:
            if dim is None or u.dim == dim:
                self._resolve_cache[cache_key] = u
                return u
            self._resolve_cache[cache_key] = None
            return None

        # Cache the miss
        self._resolve_cache[cache_key] = None
        return None

    def preferred_for(self, dim: Dimension) -> Unit | None:
        return self._preferred.get(dim)

    def set_preferred(self, unit_or_key: Unit | str) -> None:
        u = unit_or_key if isinstance(unit_or_key, Unit) else self.resolve(unit_or_key)
        if u is None:
            raise ValueError(f"Unknown unit: {unit_or_key!r}")
        self._preferred[u.dim] = u

    def names_for(self, dim: Dimension) -> list[str]:
        """All normalized names/aliases for a given dimension."""
        return sorted(self._by_dim.get(dim, {}).keys())

    def all_names(self) -> list[str]:
        """All normalized names/aliases globally (not symbols)."""
        return sorted(self._by_name.keys())

    def si_unit_for(self, dim: Dimension) -> Unit | None:
        """
        Return a sensible default display unit:
          1) preferred_for(dim)
          2) any unit with si_factor == 1 and si_offset == 0
          3) None
        """
        u = self._preferred.get(dim)
        if u is not None:
            return u
        for candidate in self._by_dim.get(dim, {}).values():
            if candidate.si_factor == 1.0 and candidate.si_offset == 0.0:
                return candidate
        return None

    # ----- Python niceties -----
    def __getattr__(self, name: str) -> Unit:
        # Guard against deepcopy and pickle operations that cause recursion
        if name in {
            '__setstate__', '__getstate__', '__getnewargs__', '__getnewargs_ex__',
            '__reduce__', '__reduce_ex__', '__copy__', '__deepcopy__',
            '__getattribute__', '__setattr__', '__delattr__',
            '__dict__', '__weakref__', '__class__'
        }:
            raise AttributeError(f"{type(self).__name__} has no attribute '{name}'")

        nk = _norm(name)
        u = self._attr_exposed.get(nk)
        if u is None:
            raise AttributeError(f"{type(self).__name__} has no attribute '{name}'")
        return u

    def __dir__(self) -> list[str]:
        std = list(super().__dir__())
        return sorted(set(std + list(self._attr_exposed.keys())))


# Single global registry
ureg = UnitRegistry()


# --------------------------
# Public "u" namespace (dot access to concrete units)
# --------------------------
class Units:
    def __init__(self):
        self.__sealed = False

    def __setattr__(self, k, v):
        if hasattr(self, "_Units__sealed") and self.__sealed:
            raise AttributeError("u is sealed; cannot modify.")
        object.__setattr__(self, k, v)


u = Units()

# For stub writer (names and aliases actually attached to `u`)
_unit_registry: dict[str, Unit] = {}
_unit_aliases: dict[str, str] = {}


# =======================
# Prefix generation
# =======================
def _generate_prefixed_units(base: Unit, *, expose_to_u: bool = False) -> None:
    """
    Create prefixed variants for a base unit, e.g., N -> kN, mN, μN ...
    - Interns by symbol so duplicates are skipped.
    - Registers each variant and optionally exposes them on `u`.
    """
    for pname, psym, pfactor in PREFIXES:
        sym = f"{psym}{base.symbol}"
        name = f"{pname}{base.name}"  # Changed from f"{pname}_{base.name}" to remove underscore

        # Already created?
        if sym in ureg._intern_by_symbol:
            continue

        aliases: set[str] = {name, sym}
        # Include ASCII 'u' alias for micro (μ)
        if psym == "μ":
            aliases.add(f"u{base.symbol}")
            aliases.add(f"micro{base.name}")  # Changed from f"micro_{base.name}" to remove underscore

        unit = Unit(name=name, symbol=sym, dim=base.dim, si_factor=base.si_factor * pfactor)
        ureg.register(unit, *aliases)

        if expose_to_u:
            # canonical name
            setattr(u, name, unit)
            _unit_registry[name] = unit
            # symbol attr (e.g., u.kN)
            setattr(u, sym, unit)
            _unit_aliases[sym] = base.name
            # ASCII micro symbol alias
            if psym == "μ":
                setattr(u, f"u{base.symbol}", unit)
                _unit_aliases[f"u{base.symbol}"] = base.name


# =======================
# Add/base units with allow_prefix
# =======================
def add_unit(
    dim_obj: Dimension,
    *,
    symbol: str,
    si_factor: float,
    si_offset: float = 0.0,
    name: str | None = None,
    aliases: Iterable[str] = (),
    allow_prefix: bool = False,
    expose_prefixed_to_u: bool = False,
) -> Unit:
    """
    Define a base unit with a canonical name and optional aliases.
    Registers the unit and exposes it on `u`.
    Optionally generates prefixed variants (kilo_, milli_, μ_, ...).
    """
    if name is None:
        name = _caller_var_name("add_unit")

    if name in _unit_registry or name in _unit_aliases:
        raise KeyError(f"Unit name '{name}' already defined.")

    unit = Unit(name=name, symbol=symbol, dim=dim_obj, si_factor=si_factor, si_offset=si_offset)
    # Also pass the canonical name and symbol as aliases into the name map (harmless; deduped)
    ureg.register(unit, name, symbol, *aliases)

    # Expose on `u`
    setattr(u, name, unit)
    _unit_registry[name] = unit
    for a in aliases:
        if a in _unit_registry or a in _unit_aliases:
            raise KeyError(f"Unit alias '{a}' already in use.")
        setattr(u, a, unit)
        _unit_aliases[a] = name

    if allow_prefix:
        _generate_prefixed_units(unit, expose_to_u=expose_prefixed_to_u)

    return unit


# =======================
# Add/composed units
# =======================
def attach_composed(
    unit: Unit,
    *,
    name: str,
    symbol: str | None = None,
    aliases: Iterable[str] = (),
    set_preferred: bool = False,
) -> Unit:
    """
    Take an already composed unit (e.g., u.lbf / (u.inch**2)), give it a canonical name/symbol,
    register it, and expose it on `u`.

    - Keeps the original dimension & si_factor of `unit`.
    - Registers both your new symbol AND the original composed symbol as aliases,
      so lookups by "psi" and "lbf/in²" both work.
    """
    # If a composed unit with this name already exists (from operator composition),
    # reuse it instead of creating a duplicate. This happens for cases like
    # u.meter / u.second where the auto-generated name is already "meter_per_second".
    existing = ureg._by_name.get(_norm(name))

    if existing is not None:
        # Ensure the existing unit matches the composed one (same dimension and factor)
        if existing.dim != unit.dim or existing.si_factor != unit.si_factor or existing.si_offset != unit.si_offset:
            raise ValueError(f"attach_composed: name '{name}' already registered for a different unit")

        # Add any new aliases (including provided symbol or the composed symbol)
        extra_aliases = set(aliases)
        if symbol is not None:
            extra_aliases.add(symbol)
        extra_aliases.add(unit.symbol)
        if extra_aliases:
            ureg.register(existing, *extra_aliases)

        # Expose on `u`
        setattr(u, name, existing)
        _unit_registry[name] = existing

        for a in aliases:
            if a in _unit_registry or a in _unit_aliases:
                continue
            setattr(u, a, existing)
            _unit_aliases[a] = name

        if set_preferred:
            ureg.set_preferred(existing)

        return existing

    # Otherwise, construct a new named unit with the requested symbol
    sym = symbol or unit.symbol
    named = Unit(name=name, symbol=sym, dim=unit.dim, si_factor=unit.si_factor, si_offset=unit.si_offset)

    # New name, new symbol, and the original composed symbol as aliases
    all_aliases = set(aliases) | {name, sym, unit.symbol}
    ureg.register(named, *all_aliases)

    setattr(u, name, named)
    _unit_registry[name] = named

    # Optionally expose extra aliases on `u` (comment out if too noisy)
    for a in aliases:
        if a in _unit_registry or a in _unit_aliases:
            continue
        setattr(u, a, named)
        _unit_aliases[a] = name

    if set_preferred:
        ureg.set_preferred(named)

    return named


# =======================
# Composition (operator overloading) with interning
# =======================
def _compose(a: Unit, b: Unit, *, div: bool) -> Unit:
    sym = f"{a.symbol}/{b.symbol}" if div else f"{a.symbol}·{b.symbol}"
    cached = ureg._intern_by_symbol.get(sym)
    if cached is not None:
        return cached

    name = f"{a.name}_per_{b.name}" if div else f"{a.name}_{b.name}"
    dimn = a.dim / b.dim if div else a.dim * b.dim
    fact = (a.si_factor / b.si_factor) if div else (a.si_factor * b.si_factor)

    return ureg.register(Unit(name=name, symbol=sym, dim=dimn, si_factor=fact))


def _pow_unit(a: Unit, k: int) -> Unit:
    if k == 1:
        return a
    sym = f"{a.symbol}{_SUP.get(k, '^' + str(k))}"
    cached = ureg._intern_by_symbol.get(sym)
    if cached is not None:
        return cached

    name = f"{a.name}_{k}"
    return ureg.register(Unit(name=name, symbol=sym, dim=(a.dim**k), si_factor=(a.si_factor**k)))


# =======================
# Stubs & sealing
# =======================
def write_units_stub(path: str = "units.pyi") -> None:
    """
    Emit a `.pyi` stub for IDEs so `u.<unit>` attributes show as Final[Unit].
    """
    with open(path, "w", encoding="utf-8") as f:
        f.write("from typing import Final\n")
        f.write("from .core import Unit\n\n")
        f.write("class Units:\n")
        for name in sorted(_unit_registry):
            f.write(f"    {name}: Final[Unit]\n")
        for alias, canonical in sorted(_unit_aliases.items()):
            f.write(f"    {alias}: Final[Unit]  # alias for {canonical}\n")
        f.write("\n")
        f.write("u: Units  # not Final; attributes are populated dynamically then sealed\n")


def seal_units() -> None:
    """
    Make both the registry and the public `u` namespace immutable.
    """
    ureg.seal()
    u.__sealed = True  # type: ignore[attr-defined]


# =======================
# UnitNamespace (declarative catalogs)
# =======================
@dataclass(frozen=True, slots=True)
class UnitDef:
    symbol: str
    dim: Dimension
    si_factor: float
    si_offset: float = 0.0
    aliases: tuple[str, ...] = ()
    allow_prefix: bool = False


class UnitNamespaceMeta(type):
    def __new__(mcls, name, bases, ns):
        cls = super().__new__(mcls, name, bases, ns)
        expose_pref = bool(ns.get("__expose_prefixed__", False))
        preferred_name = ns.get("__preferred__", None)

        created: dict[str, Unit] = {}
        for attr, val in list(ns.items()):
            if isinstance(val, UnitDef):
                unit = add_unit(
                    val.dim,
                    symbol=val.symbol,
                    si_factor=val.si_factor,
                    si_offset=val.si_offset,
                    name=attr,
                    aliases=val.aliases,
                    allow_prefix=val.allow_prefix,
                    expose_prefixed_to_u=expose_pref,
                )
                setattr(cls, attr, unit)
                created[attr] = unit
            elif isinstance(val, Unit):
                # already constructed unit
                setattr(cls, attr, val)
                created[attr] = val

        if preferred_name:
            if preferred_name not in created:
                raise KeyError(f"__preferred__='{preferred_name}' not found in {name}")
            ureg.set_preferred(created[preferred_name])

        # Freeze class (catalogs are constant after creation)
        def _blocked_setattr(self, *_a, **_k):
            raise AttributeError(f"{name} is frozen; define units in the class body.")

        cls.__setattr__ = _blocked_setattr  # type: ignore[attr-defined]
        return cls


class UnitNamespace(metaclass=UnitNamespaceMeta):
    __slots__ = ()


# =======================
# Example: ForceUnits catalog (real units)
# =======================
# NOTE: You can change __expose_prefixed__ to False if you don't want u.kN, u.mN, ...

# You can define additional catalogs similarly:
# class PressureUnits(UnitNamespace): ...
# class MassDensityUnits(UnitNamespace): ...

# =======================
# Small demo / defaults (optional)
# =======================
# if __name__ == "__main__":
#     newton = UnitDef("N",    dim.Force, si_factor=1.0,     aliases=("N","newtons"), allow_prefix=True)

#     class ForceUnits(UnitNamespace):
#         """Unit constants for Force."""
#         __slots__ = ()
#         __preferred__ = "newton"
#         __expose_prefixed__ = True  # expose kN, mN, μN, etc. on `u`

#         newton = newton
#         dyne   = UnitDef("dyn",  dim.Force, si_factor=1e-5,    aliases=("dyne","dynes"), allow_prefix=True)
#         lbf    = UnitDef("lbf",  dim.Force, si_factor=4.4482216152605, aliases=("pound_force","poundforce"))
#     # A couple of base units to make the demo nicer (define yours elsewhere if you prefer)
#     meter    = add_unit(dim.L, symbol="m",  si_factor=1.0, aliases=("meters","metre","metres"), allow_prefix=True, expose_prefixed_to_u=True)
#     second   = add_unit(dim.T, symbol="s",  si_factor=1.0, aliases=("sec","secs","seconds"),   allow_prefix=True, expose_prefixed_to_u=True)
#     kilogram = add_unit(dim.M, symbol="kg", si_factor=1.0, aliases=("kilograms","kg"))

#     # Composition still works:
#     mps = u.m / u.s  # "m/s" (composed; not auto-attached unless you do it yourself)

#     # Preferred: Force set to N by ForceUnits; set more if desired:
#     # ureg.set_preferred(u.Pa)  # once you define PressureUnits

#     # Seal when your catalogs are loaded:
#     seal_units()

#     # Quick print:
#     F = Q(1.5, u.kN)  # thanks to prefixes on newton
#     print("Force:", F)  # prints in preferred (N) by default; convert if you like: F.to(u.kN)
