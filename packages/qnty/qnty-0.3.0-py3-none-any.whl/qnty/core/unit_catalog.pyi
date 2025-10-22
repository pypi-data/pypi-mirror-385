from typing import Final

from .unit import Unit, UnitNamespace

class AccelerationUnits(UnitNamespace): ...

class AnglePlaneUnits(UnitNamespace): ...

class AreaUnits(UnitNamespace): ...

class DimensionlessUnits(UnitNamespace): ...

class EnergyUnits(UnitNamespace): ...

class ForceUnits(UnitNamespace): ...

class LengthUnits(UnitNamespace): ...

class MassDensityUnits(UnitNamespace): ...

class MassFlowRateUnits(UnitNamespace): ...

class PowerThermalDutyUnits(UnitNamespace): ...

class PressureUnits(UnitNamespace): ...

class SecondMomentOfAreaUnits(UnitNamespace): ...

class SpecificVolumeUnits(UnitNamespace): ...

class TorqueUnits(UnitNamespace): ...

class VelocityLinearUnits(UnitNamespace): ...

class ViscosityDynamicUnits(UnitNamespace): ...

class ViscosityKinematicUnits(UnitNamespace): ...

class VolumetricFlowRateUnits(UnitNamespace): ...

class Units:
    ampere: Final[Unit]
    british_thermal_unit: Final[Unit]
    british_thermal_unit_per_hour: Final[Unit]
    candela: Final[Unit]
    centiampere: Final[Unit]
    centigram: Final[Unit]
    centimeter: Final[Unit]
    centimole: Final[Unit]
    centisecond: Final[Unit]
    cubic_foot: Final[Unit]
    cubic_foot_per_minute: Final[Unit]
    cubic_foot_per_pound_mass: Final[Unit]
    cubic_meter: Final[Unit]
    cubic_meter_per_kilogram: Final[Unit]
    cubic_meter_per_second: Final[Unit]
    day: Final[Unit]
    decaampere: Final[Unit]
    decagram: Final[Unit]
    decameter: Final[Unit]
    decamole: Final[Unit]
    decasecond: Final[Unit]
    deciampere: Final[Unit]
    decigram: Final[Unit]
    decimeter: Final[Unit]
    decimole: Final[Unit]
    decisecond: Final[Unit]
    degree: Final[Unit]
    dimensionless: Final[Unit]
    erg_per_gram: Final[Unit]
    feet_per_second: Final[Unit]
    foot: Final[Unit]
    foot_per_square_second: Final[Unit]
    foot_pound_force: Final[Unit]
    foot_squared_per_second: Final[Unit]
    gallon: Final[Unit]
    gallon_per_minute: Final[Unit]
    gram: Final[Unit]
    hectoampere: Final[Unit]
    hectogram: Final[Unit]
    hectometer: Final[Unit]
    hectomole: Final[Unit]
    hectosecond: Final[Unit]
    horsepower: Final[Unit]
    hour: Final[Unit]
    inch: Final[Unit]
    inch_pound_force: Final[Unit]
    inch_quadrupled: Final[Unit]
    joule: Final[Unit]
    kelvin: Final[Unit]
    kiloampere: Final[Unit]
    kilogram: Final[Unit]
    kilogram_per_cubic_meter: Final[Unit]
    kilogram_per_second: Final[Unit]
    kilometer: Final[Unit]
    kilomole: Final[Unit]
    kilosecond: Final[Unit]
    liter: Final[Unit]
    meter: Final[Unit]
    meter_per_second: Final[Unit]
    meter_per_square_second: Final[Unit]
    microampere: Final[Unit]
    microgram: Final[Unit]
    micrometer: Final[Unit]
    micromole: Final[Unit]
    microsecond: Final[Unit]
    milli_liter: Final[Unit]
    milliampere: Final[Unit]
    milligram: Final[Unit]
    millimeter: Final[Unit]
    millimeter_quadrupled: Final[Unit]
    millimole: Final[Unit]
    million_british_thermal_unit: Final[Unit]
    millisecond: Final[Unit]
    minute: Final[Unit]
    mole: Final[Unit]
    nanoampere: Final[Unit]
    nanogram: Final[Unit]
    nanometer: Final[Unit]
    nanomole: Final[Unit]
    nanosecond: Final[Unit]
    newton: Final[Unit]
    newton_meter: Final[Unit]
    ounce: Final[Unit]
    ounce_per_milliliter: Final[Unit]
    pascal: Final[Unit]
    pascal_second: Final[Unit]
    poise: Final[Unit]
    pound_force: Final[Unit]
    pound_force_per_square_inch: Final[Unit]
    pound_force_second_per_square_foot: Final[Unit]
    pound_mass: Final[Unit]
    pound_mass_per_cubic_foot: Final[Unit]
    radian: Final[Unit]
    second: Final[Unit]
    slug: Final[Unit]
    square_foot: Final[Unit]
    square_meter: Final[Unit]
    square_meter_per_second: Final[Unit]
    square_millimeter: Final[Unit]
    thousand_british_thermal_unit: Final[Unit]
    watt: Final[Unit]
    year: Final[Unit]
    Btu: Final[Unit]  # alias for british_thermal_unit
    Btu_per_hour: Final[Unit]  # alias for british_thermal_unit_per_hour
    J: Final[Unit]  # alias for joule
    MBtu: Final[Unit]  # alias for thousand_british_thermal_unit
    MMBtu: Final[Unit]  # alias for million_british_thermal_unit
    N: Final[Unit]  # alias for newton
    Pa: Final[Unit]  # alias for pascal
    W: Final[Unit]  # alias for watt
    amp: Final[Unit]  # alias for ampere
    amperes: Final[Unit]  # alias for ampere
    amps: Final[Unit]  # alias for ampere
    cA: Final[Unit]  # alias for ampere
    cg: Final[Unit]  # alias for gram
    cm: Final[Unit]  # alias for meter
    cmol: Final[Unit]  # alias for mole
    cs: Final[Unit]  # alias for second
    cubic_feet: Final[Unit]  # alias for cubic_foot
    cubic_feet_per_minute: Final[Unit]  # alias for cubic_foot_per_minute
    cubic_feet_per_pound_mass: Final[Unit]  # alias for cubic_foot_per_pound_mass
    cubic_meters: Final[Unit]  # alias for cubic_meter
    cubic_meters_per_kilogram: Final[Unit]  # alias for cubic_meter_per_kilogram
    cubic_meters_per_second: Final[Unit]  # alias for cubic_meter_per_second
    dA: Final[Unit]  # alias for ampere
    daA: Final[Unit]  # alias for ampere
    dag: Final[Unit]  # alias for gram
    dam: Final[Unit]  # alias for meter
    damol: Final[Unit]  # alias for mole
    das: Final[Unit]  # alias for second
    days: Final[Unit]  # alias for day
    deg: Final[Unit]  # alias for degree
    degrees: Final[Unit]  # alias for degree
    dg: Final[Unit]  # alias for gram
    dm: Final[Unit]  # alias for meter
    dmol: Final[Unit]  # alias for mole
    ds: Final[Unit]  # alias for second
    feet: Final[Unit]  # alias for foot
    feet_per_second_squared: Final[Unit]  # alias for foot_per_square_second
    feet_per_square_second: Final[Unit]  # alias for foot_per_square_second
    feet_squared_per_second: Final[Unit]  # alias for foot_squared_per_second
    foot_per_second_squared: Final[Unit]  # alias for foot_per_square_second
    ft: Final[Unit]  # alias for foot
    ft2: Final[Unit]  # alias for square_foot
    ft3: Final[Unit]  # alias for cubic_foot
    ft_per_s: Final[Unit]  # alias for feet_per_second
    gal: Final[Unit]  # alias for gallon
    gallons: Final[Unit]  # alias for gallon
    gpm: Final[Unit]  # alias for gallon_per_minute
    grams: Final[Unit]  # alias for gram
    hA: Final[Unit]  # alias for ampere
    hg: Final[Unit]  # alias for gram
    hm: Final[Unit]  # alias for meter
    hmol: Final[Unit]  # alias for mole
    hs: Final[Unit]  # alias for second
    inches: Final[Unit]  # alias for inch
    joules: Final[Unit]  # alias for joule
    kA: Final[Unit]  # alias for ampere
    kg: Final[Unit]  # alias for gram
    kg_per_m3: Final[Unit]  # alias for kilogram_per_cubic_meter
    kilograms_per_second: Final[Unit]  # alias for kilogram_per_second
    km: Final[Unit]  # alias for meter
    kmol: Final[Unit]  # alias for mole
    ks: Final[Unit]  # alias for second
    lbf: Final[Unit]  # alias for pound_force
    lbm: Final[Unit]  # alias for pound_mass
    lbm_per_ft3: Final[Unit]  # alias for pound_mass_per_cubic_foot
    liters: Final[Unit]  # alias for liter
    litre: Final[Unit]  # alias for liter
    litres: Final[Unit]  # alias for liter
    m2: Final[Unit]  # alias for square_meter
    m3: Final[Unit]  # alias for cubic_meter
    mA: Final[Unit]  # alias for ampere
    meters: Final[Unit]  # alias for meter
    meters_per_second: Final[Unit]  # alias for meter_per_second
    meters_per_square_second: Final[Unit]  # alias for meter_per_square_second
    metre: Final[Unit]  # alias for meter
    metres: Final[Unit]  # alias for meter
    mg: Final[Unit]  # alias for gram
    milliliters: Final[Unit]  # alias for milli_liter
    millilitre: Final[Unit]  # alias for milli_liter
    millilitres: Final[Unit]  # alias for milli_liter
    minutes: Final[Unit]  # alias for minute
    mm: Final[Unit]  # alias for meter
    mm2: Final[Unit]  # alias for square_millimeter
    mmol: Final[Unit]  # alias for mole
    moles: Final[Unit]  # alias for mole
    ms: Final[Unit]  # alias for second
    nA: Final[Unit]  # alias for ampere
    newtons: Final[Unit]  # alias for newton
    ng: Final[Unit]  # alias for gram
    nm: Final[Unit]  # alias for meter
    nmol: Final[Unit]  # alias for mole
    ns: Final[Unit]  # alias for second
    ounces: Final[Unit]  # alias for ounce
    oz_per_mL: Final[Unit]  # alias for ounce_per_milliliter
    pascal_seconds: Final[Unit]  # alias for pascal_second
    pascals: Final[Unit]  # alias for pascal
    poundforce: Final[Unit]  # alias for pound_force
    radians: Final[Unit]  # alias for radian
    seconds: Final[Unit]  # alias for second
    slugs: Final[Unit]  # alias for slug
    square_feet: Final[Unit]  # alias for square_foot
    square_meters: Final[Unit]  # alias for square_meter
    square_meters_per_second: Final[Unit]  # alias for square_meter_per_second
    uA: Final[Unit]  # alias for ampere
    ug: Final[Unit]  # alias for gram
    um: Final[Unit]  # alias for meter
    umol: Final[Unit]  # alias for mole
    unitless: Final[Unit]  # alias for dimensionless
    us: Final[Unit]  # alias for second
    watts: Final[Unit]  # alias for watt
    years: Final[Unit]  # alias for year

u: Units  # not Final; attributes are populated dynamically then sealed
