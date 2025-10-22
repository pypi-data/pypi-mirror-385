"""
Simplified quantity definition using metaclass for the unified Quantity design.
"""

import sys
from typing import Any, TypeVar, cast

from .quantity import Quantity, QuantitySetter, UnitApplier, UnitChanger
from .unit import UnitNamespace

D = TypeVar("D")


def _get_namespace_dim(unit_ns: type[UnitNamespace]):
    """Get dimension from a UnitNamespace."""
    # Find any unit in the namespace and get its dimension
    for attr_name in dir(unit_ns):
        if not attr_name.startswith("_"):
            attr = getattr(unit_ns, attr_name)
            if hasattr(attr, "dim"):
                return attr.dim
    raise ValueError(f"No dimension found in {unit_ns}")


def bind_quantity_namespace(quantity_cls: type, setter_cls: type, unit_ns: type[UnitNamespace]):
    """Bind unit namespace methods to quantity and setter classes."""
    # Add unit methods to setter class
    for attr_name in dir(unit_ns):
        if not attr_name.startswith("_"):
            unit = getattr(unit_ns, attr_name)
            if hasattr(unit, "dim"):

                def make_setter_method(u):
                    def method(self):
                        return self._owner.set(self._value, u)

                    return property(method)

                setattr(setter_cls, attr_name, make_setter_method(unit))


class QuantityMeta(type):
    """Metaclass that creates specialized quantity classes."""

    def __new__(mcs, name: str, bases: tuple, namespace: dict):
        # Only process subclasses that have UNIT_NS defined
        if "UNIT_NS" in namespace:
            unit_ns = namespace["UNIT_NS"]
            dim = _get_namespace_dim(unit_ns)

            # Create setter class
            setter_cls_name = f"{name}Setter"
            setter_cls = type(setter_cls_name, (QuantitySetter,), {"__slots__": ()})
            namespace["SETTER_CLS"] = setter_cls

            # Create ToUnit and AsUnit inner classes
            to_unit_cls = type("ToUnit", (UnitApplier,), {"__slots__": ()})
            as_unit_cls = type("AsUnit", (UnitChanger,), {"__slots__": ()})
            namespace["ToUnit"] = to_unit_cls
            namespace["AsUnit"] = as_unit_cls

            # Override __init__ to use the correct dimension
            def __init__(self, name: str, value: float | None = None, preferred=None):
                # Initialize with correct order: name first, then dim (captured from closure)
                # Call the dataclass __init__ directly
                object.__setattr__(self, "name", name)
                object.__setattr__(self, "dim", dim)
                object.__setattr__(self, "value", value)
                object.__setattr__(self, "preferred", preferred)

            namespace["__init__"] = __init__

            # Add properties
            if "to_unit" not in namespace:

                def to_unit_prop(self):
                    return self.ToUnit(self)

                namespace["to_unit"] = property(to_unit_prop)

            if "as_unit" not in namespace:

                def as_unit_prop(self):
                    return self.AsUnit(self)

                namespace["as_unit"] = property(as_unit_prop)

            # Override set method to use specialized setter and return correct type
            if "set" not in namespace:

                def set_method(self, value: float, unit=None):
                    if unit is None:
                        return self.SETTER_CLS(self, value)

                    # Convert unit if it's a string
                    from .unit import ureg

                    if isinstance(unit, str):
                        resolved = ureg.resolve(unit)
                        if resolved is None:
                            raise ValueError(f"Unknown unit '{unit}'")
                        unit = resolved

                    # Create new instance of the same specialized type
                    new_instance = type(self)(self.name, value=unit.si_factor * value + unit.si_offset, preferred=self.preferred or unit)
                    return new_instance

                namespace["set"] = set_method

        # Create the class
        cls = super().__new__(mcs, name, bases, namespace)

        # Bind namespace after class creation
        if hasattr(cls, "UNIT_NS") and hasattr(cls, "SETTER_CLS"):
            typed_cls = cast(Any, cls)
            bind_quantity_namespace(typed_cls, typed_cls.SETTER_CLS, typed_cls.UNIT_NS)
            # Store setter in module namespace for export
            if hasattr(cls, "__module__"):
                module = sys.modules[cls.__module__]
                setattr(module, typed_cls.SETTER_CLS.__name__, typed_cls.SETTER_CLS)

        return cls


class TypedQuantity(Quantity[D], metaclass=QuantityMeta):
    """Base class for typed quantities with automatic boilerplate generation."""

    __slots__ = ()

    # These will be set by metaclass
    UNIT_NS: type[UnitNamespace]
    SETTER_CLS: type[QuantitySetter]

    def __init__(self, name: str, value: float | None = None, preferred=None) -> None:
        """Override to provide correct signature - implementation will be replaced by metaclass."""
        ...

    class ToUnit(UnitApplier):
        __slots__ = ()

    class AsUnit(UnitChanger):
        __slots__ = ()


def quantity(unit_namespace: type[UnitNamespace]):
    """
    Decorator to create a quantity class with minimal boilerplate.

    Usage:
        @quantity(LengthUnits)
        class Length:
            pass
    """

    def wrapper(cls):
        # Get the class name
        class_name = cls.__name__

        # Create a new class that inherits from TypedQuantity
        new_cls = type(
            class_name,
            (TypedQuantity,),
            {
                "__slots__": getattr(cls, "__slots__", ()),
                "UNIT_NS": unit_namespace,
                "__module__": cls.__module__,
                "__qualname__": cls.__qualname__,
                "__doc__": cls.__doc__,
            },
        )

        # Copy any additional attributes from the original class
        for attr_name in dir(cls):
            if not attr_name.startswith("__"):
                setattr(new_cls, attr_name, getattr(cls, attr_name))

        return new_cls

    return wrapper
