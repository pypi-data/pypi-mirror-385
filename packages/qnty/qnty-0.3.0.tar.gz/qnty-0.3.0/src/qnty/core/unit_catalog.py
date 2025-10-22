import math
from typing import TYPE_CHECKING, Final

from .dimension_catalog import dim
from .unit import Unit, UnitNamespace, add_unit, attach_composed, u

if TYPE_CHECKING:
    from . import u

# dimensionless unit
dimensionless = add_unit(
    dim.D,
    symbol="",
    si_factor=1.0,
    aliases=("unitless",),
)

# region // Absorbed Radiation Dose
erg_per_gram = add_unit(
    dim.ABSORBED_RADIATION_DOSE,
    symbol="erg/g",
    si_factor=0.0001,
)

# endregion // Absorbed Radiation Dose

radian = add_unit(
    dim.D,
    symbol="rad",
    si_factor=1.0,
    aliases=("radians",),
)

degree = add_unit(
    dim.D,
    symbol="°",
    si_factor=math.pi / 180.0,
    aliases=(
        "degrees",
        "deg",
    ),
)


class AnglePlaneUnits(UnitNamespace):
    __slots__ = ()
    __preferred__ = "radian"

    radian: Final[Unit] = radian
    degree: Final[Unit] = degree


# ==============
# TIME
# ==============
second = add_unit(dim.T, symbol="s", si_factor=1.0, aliases=("seconds",), allow_prefix=True, expose_prefixed_to_u=True)

minute = add_unit(
    dim.T,
    symbol="min",
    si_factor=60.0,
    aliases=("minutes",),
)

hour = add_unit(
    dim.T,
    symbol="h",
    si_factor=3600.0,
)

day = add_unit(
    dim.T,
    symbol="d",
    si_factor=86400.0,
    aliases=("days",),
)

year = add_unit(
    dim.T,
    symbol="yr",
    si_factor=31557600.0,
    aliases=("years",),
)

# ==============
# LENGTH
# ==============
meter = add_unit(
    dim.L,
    symbol="m",
    si_factor=1.0,
    aliases=(
        "meters",
        "metre",
        "metres",
    ),
    allow_prefix=True,
    expose_prefixed_to_u=True,
)

inch = add_unit(
    dim.L,
    symbol="in",
    si_factor=0.0254,
    aliases=("inches",),
)

foot = add_unit(
    dim.L,
    symbol="ft",
    si_factor=0.3048,
    aliases=(
        "feet",
        "ft",
    ),
)


class LengthUnits(UnitNamespace):
    __slots__ = ()
    __preferred__ = "meter"

    meter: Final[Unit] = meter
    millimeter: Final[Unit] = u.millimeter
    inch: Final[Unit] = inch
    foot: Final[Unit] = foot


# ==============
# MASS
# ==============
gram = add_unit(dim.M, symbol="g", si_factor=1e-3, aliases=("grams",), allow_prefix=True, expose_prefixed_to_u=True)

pound_mass = add_unit(
    dim.M,
    symbol="lbm",
    si_factor=0.45359237,
    aliases=("lbm",),
)

slug = add_unit(
    dim.M,
    symbol="slug",
    si_factor=14.59390293720636,
    aliases=("slugs",),
)

ounce = add_unit(
    dim.M,
    symbol="oz",
    si_factor=0.028349523125,
    aliases=("ounces",),
)

# ==============
# TEMPERATURE
# ==============
kelvin = add_unit(
    dim.Θ,
    symbol="K",
    si_factor=1.0,
)

# ==============
# LUMINOUS INTENSITY
# ==============
candela = add_unit(
    dim.J,
    symbol="cd",
    si_factor=1.0,
)

# ==============
# ELECTRIC CURRENT
# ==============
ampere = add_unit(
    dim.A,
    symbol="A",
    si_factor=1.0,
    aliases=(
        "amperes",
        "amps",
        "amp",
    ),
    allow_prefix=True,
    expose_prefixed_to_u=True,
)

# ==============
# AMOUNT OF SUBSTANCE
# ==============
mole = add_unit(dim.N, symbol="mol", si_factor=1.0, aliases=("moles",), allow_prefix=True, expose_prefixed_to_u=True)


class DimensionlessUnits(UnitNamespace):
    __slots__ = ()
    __preferred__ = ""

    dimensionless: Final[Unit] = dimensionless


###############################################
# SECONDARY UNITS
###############################################

# =======================
# VELOCITY
# =======================
meter_per_second = attach_composed(
    u.meter / u.second,
    name="meter_per_second",
    symbol="m/s",
    aliases=(
        "meters_per_second",
        "m/s",
    ),
)

feet_per_second = attach_composed(
    u.foot / u.second,
    name="feet_per_second",
    symbol="ft/s",
    aliases=(
        "ft_per_s",
        "ft/s",
    ),
)


class VelocityLinearUnits(UnitNamespace):
    __slots__ = ()
    __preferred__ = "meter_per_second"

    meter_per_second: Final[Unit] = meter_per_second
    feet_per_second: Final[Unit] = feet_per_second


# =======================
# ACCELERATION
# =======================
meter_per_square_second = attach_composed(
    u.meter / (u.second**2),
    name="meter_per_square_second",
    symbol="m/s²",
    aliases=(
        "meter_per_square_second",
        "meters_per_square_second",
        "m/s2",
    ),
)

foot_per_square_second = attach_composed(
    u.foot / (u.second**2),
    name="foot_per_square_second",
    symbol="ft/s²",
    aliases=(
        "foot_per_square_second",
        "feet_per_square_second",
        "foot_per_second_squared",
        "feet_per_second_squared",
        "ft/s2",
    ),
)


class AccelerationUnits(UnitNamespace):
    __slots__ = ()
    # Preferred must reference the attribute name, not the symbol
    __preferred__ = "meter_per_square_second"

    meter_per_square_second: Final[Unit] = meter_per_square_second
    foot_per_square_second: Final[Unit] = foot_per_square_second


# =======================
# AREA
# =======================
square_meter = attach_composed(
    u.meter**2,
    name="square_meter",
    symbol="m²",
    aliases=(
        "square_meter",
        "square_meters",
        "m2",
    ),
)

square_millimeter = attach_composed(
    u.millimeter**2,
    name="square_millimeter",
    symbol="mm²",
    aliases=("mm2",),
)

square_foot = attach_composed(
    u.foot**2,
    name="square_foot",
    symbol="ft²",
    aliases=(
        "square_foot",
        "square_feet",
        "ft2",
    ),
)


class AreaUnits(UnitNamespace):
    __slots__ = ()
    __preferred__ = "square_meter"

    square_meter: Final[Unit] = square_meter
    square_foot: Final[Unit] = square_foot
    square_millimeter: Final[Unit] = square_millimeter


# NOTE: VOLUME UNITS BELOW
cubic_meter = attach_composed(
    u.meter**3,
    name="cubic_meter",
    symbol="m³",
    aliases=(
        "cubic_meter",
        "cubic_meters",
        "m3",
    ),
)

# TODO: Add option to add prefixes to composed units
liter = attach_composed(
    u.decimeter**3,
    name="liter",
    symbol="L",
    aliases=(
        "liters",
        "litre",
        "litres",
    ),
)

milli_liter = attach_composed(
    u.centimeter**3,
    name="milli_liter",
    symbol="mL",
    aliases=("milliliters", "millilitre", "millilitres"),
)

gallon = add_unit(
    dim.L**3,
    symbol="gal",
    si_factor=0.003785411784,
    aliases=("gallons", "gal"),
)

cubic_foot = attach_composed(
    u.foot**3,
    name="cubic_foot",
    symbol="ft³",
    aliases=(
        "cubic_foot",
        "cubic_feet",
        "ft3",
    ),
)

# =======================
# SOLID ANGLE
# =======================


# =======================
# PLANE ANGLE
# =======================


###############################################
# DERIVED UNITS
###############################################

# =======================
# FORCE
# =======================
newton = attach_composed(
    u.kg * u.meter / (u.second**2),
    name="newton",
    symbol="N",
    aliases=(
        "newtons",
        "N",
    ),
)

# US customary force unit
pound_force = add_unit(
    dim.FORCE,
    symbol="lbf",
    si_factor=4.4482216152605,
    aliases=("poundforce", "lbf"),
)

class ForceUnits(UnitNamespace):
    __slots__ = ()
    __preferred__ = "newton"

    newton: Final[Unit] = newton
    pound_force: Final[Unit] = pound_force


# =======================
# PRESSURE
# =======================
pascal = attach_composed(
    u.newton / (u.meter**2),
    name="pascal",
    symbol="Pa",
    aliases=(
        "pascals",
        "Pa",
    ),
)

pound_force_per_square_inch = attach_composed(
    u.pound_force / (u.inch**2),
    name="pound_force_per_square_inch",
    symbol="psi",
)


class PressureUnits(UnitNamespace):
    __slots__ = ()
    __preferred__ = "Pa"

    Pa: Final[Unit] = pascal
    pascal: Final[Unit] = pascal
    pascals: Final[Unit] = pascal
    pound_force_per_square_inch: Final[Unit] = pound_force_per_square_inch


# =======================
# STRESS
# =======================


# =======================
# ENERGY
# =======================


# =======================
# WORK
# =======================


# =======================
# POWER
# =======================

# =======================
# ENERGY FLOW
# =======================


# =======================
# HEAT FLOW
# =======================


# =======================
# MASS DENSITY
# =======================
kilogram_per_cubic_meter = attach_composed(
    u.kg / (u.meter**3),
    name="kilogram_per_cubic_meter",
    symbol="kg/m³",
    aliases=(
        "kg_per_m3",
        "kg/m3",
    ),
)

pound_mass_per_cubic_foot = attach_composed(
    u.pound_mass / (u.foot**3),
    name="pound_mass_per_cubic_foot",
    symbol="lbm/ft³",
    aliases=(
        "lbm_per_ft3",
        "lbm/ft3",
    ),
)

ounce_per_milliliter = attach_composed(
    u.ounce / u.milli_liter,
    name="ounce_per_milliliter",
    symbol="oz/mL",
    aliases=(
        "oz_per_mL",
        "oz/mL",
    ),
)


class MassDensityUnits(UnitNamespace):
    __slots__ = ()
    __preferred__ = "kilogram_per_cubic_meter"

    kilogram_per_cubic_meter: Final[Unit] = kilogram_per_cubic_meter
    pound_mass_per_cubic_foot: Final[Unit] = pound_mass_per_cubic_foot
    ounce_per_milliliter: Final[Unit] = ounce_per_milliliter



# region // Second Moment of Area

inch_quadrupled = attach_composed(
    u.inch**4,
    name="inch_quadrupled",
    symbol="in⁴",
)

mm_quadrupled = attach_composed(
    u.millimeter**4,
    name="millimeter_quadrupled",
    symbol="mm⁴",
)

class SecondMomentOfAreaUnits(UnitNamespace):
    __slots__ = ()
    __preferred__ = "inch_quadrupled"

    inch_quadrupled: Final[Unit] = inch_quadrupled
    millimeter_quadrupled: Final[Unit] = mm_quadrupled

# endregion // Second Moment of Area




# region // Torque
newton_meter = attach_composed(
    u.newton * u.meter,
    name="newton_meter",
    symbol="N·m",
    aliases=(
        "N*m",
    ),
)

inch_pound_force = attach_composed(
    u.pound_force * u.inch,
    name="inch_pound_force",
    symbol="in·lbf",
    aliases=(
        "in*lbf",
    ),
)

foot_pound_force = attach_composed(
    u.pound_force * u.foot,
    name="foot_pound_force",
    symbol="ft·lbf",
    aliases=(
        "ft*lbf",
    ),
)

class TorqueUnits(UnitNamespace):
    __slots__ = ()
    __preferred__ = "newton_meter"

    newton_meter: Final[Unit] = newton_meter
    inch_pound_force: Final[Unit] = inch_pound_force
    foot_pound_force: Final[Unit] = foot_pound_force


cubic_meter_per_second = attach_composed(
    u.meter**3 / u.second,
    name="cubic_meter_per_second",
    symbol="m³/s",
    aliases=(
        "cubic_meter_per_second",
        "cubic_meters_per_second",
        "m3/s",
    ),
)

gallon_per_minute = attach_composed(
    u.gallon / u.minute,
    name="gallon_per_minute",
    symbol="gal/min",
    aliases=("gpm",),
)

cubic_foot_per_minute = attach_composed(
    u.cubic_foot / u.minute,
    name="cubic_foot_per_minute",
    symbol="ft³/min",
    aliases=(
        "cubic_foot_per_minute",
        "cubic_feet_per_minute",
        "ft³/min",
        "ft3/min",
    ),
)


class VolumetricFlowRateUnits(UnitNamespace):
    __slots__ = ()
    __preferred__ = "cubic_meter_per_second"

    cubic_meter_per_second: Final[Unit] = cubic_meter_per_second
    gallon_per_minute: Final[Unit] = gallon_per_minute
    cubic_foot_per_minute: Final[Unit] = cubic_foot_per_minute


pascal_second = attach_composed(
    u.pascal * u.second,
    name="pascal_second",
    symbol="Pa·s",
    aliases=(
        "pascal_second",
        "pascal_seconds",
        "Pa·s",
        "Pa.s",
    ),
)

poise = attach_composed(
    u.gram / (u.centimeter * u.second),
    name="poise",
    symbol="P",
)

pound_force_second_per_square_foot = attach_composed(
    u.pound_force * u.second / (u.foot**2),
    name="pound_force_second_per_square_foot",
    symbol="lbf·s/ft²",
    aliases=(
        "lbf·s/ft²",
        "lbf*s/ft2",
    ),
)


class ViscosityDynamicUnits(UnitNamespace):
    __slots__ = ()
    __preferred__ = "pascal_second"

    pascal_second: Final[Unit] = pascal_second
    poise: Final[Unit] = poise
    pound_force_second_per_square_foot: Final[Unit] = pound_force_second_per_square_foot


square_meter_per_second = attach_composed(
    u.meter**2 / u.second,
    name="square_meter_per_second",
    symbol="m²/s",
    aliases=(
        "square_meter_per_second",
        "square_meters_per_second",
        "m2/s",
    ),
)
foot_squared_per_second = attach_composed(
    u.foot**2 / u.second,
    name="foot_squared_per_second",
    symbol="ft²/s",
    aliases=(
        "foot_squared_per_second",
        "feet_squared_per_second",
        "ft2/s",
    ),
)


class ViscosityKinematicUnits(UnitNamespace):
    __slots__ = ()
    __preferred__ = "square_meter_per_second"

    square_meter_per_second: Final[Unit] = square_meter_per_second
    foot_squared_per_second: Final[Unit] = foot_squared_per_second


# region // E

# region // ENERGY, HEAT, WORK
# Note: Using add_unit instead of attach_composed to avoid conflict
# between N·m (newton-meter) and nm (nano-meter) after normalization
joule = add_unit(
    dim.ENERGY,
    symbol="J",
    si_factor=1.0,
    aliases=(
        "joules",
        "J",
    ),
)

Btu = add_unit(
    dim.ENERGY,
    symbol="Btu",
    si_factor=1055.05585262,
    name="british_thermal_unit",
    aliases=("Btu",),
)

MBtu = add_unit(
    dim.ENERGY,
    symbol="MBtu",
    si_factor=1.05505585262e6,
    name="thousand_british_thermal_unit",
    aliases=("MBtu",),
)

MMBtu = add_unit(
    dim.ENERGY,
    symbol="MMBtu",
    si_factor=0.00105505585262e9,
    name="million_british_thermal_unit",
    aliases=("MMBtu",),
)


class EnergyUnits(UnitNamespace):
    __slots__ = ()
    __preferred__ = "joule"

    joule: Final[Unit] = joule
    Btu: Final[Unit] = Btu
    MBtu: Final[Unit] = MBtu
    MMBtu: Final[Unit] = MMBtu


# endregion // ENERGY, HEAT, WORK

# endregion // E


# region // M

# region // MASS FLOW RATE
kilogram_per_second = attach_composed(
    u.kg / u.second,
    name="kilogram_per_second",
    symbol="kg/s",
    aliases=(
        "kilogram_per_second",
        "kilograms_per_second",
        "kg/s",
    ),
)


class MassFlowRateUnits(UnitNamespace):
    __slots__ = ()
    __preferred__ = "kilogram_per_second"

    kilogram_per_second: Final[Unit] = kilogram_per_second


# region // P

# region // POWER THERMAL DUTY
watt = attach_composed(
    u.joule / u.second,
    name="watt",
    symbol="W",
    aliases=(
        "watts",
        "W",
    ),
)

Btu_per_hour = attach_composed(
    u.Btu / u.hour,
    name="british_thermal_unit_per_hour",
    symbol="Btu/h",
    aliases=(
        "Btu_per_hour",
        "Btu/h",
    ),
)

horsepower = add_unit(
    dim.POWER_THERMAL,
    symbol="hp",
    si_factor=745.69987158227,
)


class PowerThermalDutyUnits(UnitNamespace):
    __slots__ = ()
    __preferred__ = "watt"

    watt: Final[Unit] = watt
    horsepower: Final[Unit] = horsepower
    Btu_per_hour: Final[Unit] = Btu_per_hour


# endregion // POWER THERMAL DUTY

# endregion // P


# region // S


class SpecificVolumeUnits(UnitNamespace):
    __slots__ = ()
    __preferred__ = "cubic_meter_per_kilogram"

    cubic_meter_per_kilogram: Final[Unit] = attach_composed(
        u.meter**3 / u.kg,
        name="cubic_meter_per_kilogram",
        symbol="m³/kg",
        aliases=(
            "cubic_meter_per_kilogram",
            "cubic_meters_per_kilogram",
            "m3/kg",
        ),
    )

    cubic_foot_per_pound_mass: Final[Unit] = attach_composed(
        u.foot**3 / u.pound_mass,
        name="cubic_foot_per_pound_mass",
        symbol="ft³/lbm",
        aliases=(
            "cubic_foot_per_pound_mass",
            "cubic_feet_per_pound_mass",
            "ft3/lbm",
        ),
    )


# endregion // S


# region // V


# endregion // V
