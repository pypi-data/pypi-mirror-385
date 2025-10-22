from qnty.core.dimension import add_derived, add_dimension, dim

# Canonical dimensionless (all zeros) — prime code becomes (1, 1)
D = add_dimension((0, 0, 0, 0, 0, 0, 0), aliases=("DIMENSIONLESS", "DLESS", "SCALAR"))

# (L,M,T,I,Θ,N,J)

# Common bases (name and aliases are up to you)
L = add_dimension((1, 0, 0, 0, 0, 0, 0))  # Length
M = add_dimension((0, 1, 0, 0, 0, 0, 0))  # Mass
T = add_dimension((0, 0, 1, 0, 0, 0, 0))  # Time
A = add_dimension((0, 0, 0, 1, 0, 0, 0))  # Electric Current
Θ = add_dimension((0, 0, 0, 0, 1, 0, 0))  # Temperature
N = add_dimension((0, 0, 0, 0, 0, 1, 0))  # Amount of Substance
J = add_dimension((0, 0, 0, 0, 0, 0, 1))  # Luminous Intensity

# region // A
ABSORBED_RADIATION_DOSE = add_derived(L**2 * T**-2, aliases=("absorbed_radiation_dose",))

ACCELERATION = add_derived(L * T**-2, aliases=("acceleration",))

ACTIVATION_ENERGY = add_derived(L**2 * N**-1 * T**-2, aliases=("activation_energy",))

AMOUNT_OF_SUBSTANCE = add_derived(N, aliases=("amount_of_substance",))

ANGLE_PLANE = add_derived(D, aliases=("angle_plane",))

ANGLE_SOLID = add_derived(D, aliases=("angle_solid",))

ANGULAR_ACCELERATION = add_derived(T**-2, aliases=("angular_acceleration",))

ANGULAR_MOMENTUM = add_derived(M * L**2 * T**-1, aliases=("angular_momentum",))

AREA = add_derived(L**2, aliases=("area",))

AREA_PER_UNIT_VOLUME = add_derived(L**-1, aliases=("area_per_unit_volume",))

ATOMIC_WEIGHT = add_derived(M * N**-1, aliases=("atomic_weight",))

# endregion // A

# region // B

# endregion // B

# region // C

CONCENTRATION = add_derived(M * L**-3, aliases=("concentration",))

# endregion // C

# region // D

DYNAMIC_FLUIDITY = add_derived(T * L * M**-1, aliases=("dynamic_fluidity",))

# endregion // D

# region // E

ELECTRIC_CAPACITANCE = add_derived(T**4 * A**2 * L**-2 * M**-1, aliases=("electric_capacitance",))

ELECTRIC_CHARGE = add_derived(T * A * N**-1, aliases=("electric_charge",))

ELECTRIC_CURRENT_INTENSITY = add_derived(A, aliases=("electric_current_intensity",))

ELECTRIC_DIPLOE_MOMENT = add_derived(A * L * T, aliases=("electric_diploe_moment",))

ELECTRIC_FIELD_STRENGTH = add_derived(M * L * T**-3 * A**-1, aliases=("electric_field_strength",))

ELECTRIC_INDUCTANCE = add_derived(M * L**2 * T**-2 * A**-2, aliases=("electric_inductance",))

ELECTRIC_POTENTIAL = add_derived(M * L**2 * T**-3 * A**-1, aliases=("electric_potential",))

ELECTRIC_RESISTANCE = add_derived(M * L**2 * T**-3 * A**-2, aliases=("electric_resistance",))

ELECTRIC_CONDUCTANCE = add_derived(T**3 * A**2 * M**-1 * L**-2, aliases=("electric_conductance",))

ELECTRIC_PERMITTIVITY = add_derived(A**2 * T**4 * M**-1 * L**-3, aliases=("electric_permittivity",))

ELECTRIC_RESISTIVITY = add_derived(M * L**3 * T**-3 * A**-2, aliases=("electric_resistivity",))

ENERGY_FLUX = add_derived(M * T**-3, aliases=("energy_flux",))

ENERGY_PER_UNIT_AREA = add_derived(M * T**-2, aliases=("energy_per_unit_area",))

ENERGY = add_derived(
    M * L**2 * T**-2,
    aliases=(
        "energy",
        "HEAT",
        "heat",
        "WORK",
        "work",
    ),
)

# endregion // E

# region // F

FORCE = add_derived(M * L * T**-2, aliases=("force",))

FORCE_BODY = add_derived(M * L * T**-2 * L**-3, aliases=("force_body",))

FORCE_PER_UNIT_MASS = add_derived(L * T**-2, aliases=("force_per_unit_mass",))

FREQUENCY_VOLTAGE_RATIO = add_derived(T**3 * A * M**-1 * L**-2, aliases=("frequency_voltage_ratio",))

FUEL_CONSUMPTION = add_derived(L**-2, aliases=("fuel_consumption",))

# endregion // F

# region // G

# endregion // G

# region // H

HEAT_OF_COMBUSTION = add_derived(L**2 * T**-2, aliases=("heat_of_combustion",))

HEAT_OF_FUSION = add_derived(L**2 * T**-2, aliases=("heat_of_fusion",))

HEAT_OF_VAPORIZATION = add_derived(L**2 * T**-2, aliases=("heat_of_vaporization",))

HEAT_TRANSFER_COEFFICIENT = add_derived(M * T**-3 * Θ**-1, aliases=("heat_transfer_coefficient",))

# endregion // H

# region // I

ILLUMINANCE = add_derived(J * L**-2, aliases=("illuminance",))

# endregion // I

# region // J

# endregion // J

# region // K

KINETIC_ENERGY_OF_TURBULENCE = add_derived(L**2 * T**-2, aliases=("kinetic_energy_of_turbulence",))

# endregion // K

# region // L

LENGTH = add_derived(L, aliases=("length",))

LINEAR_MASS_DENSITY = add_derived(M * L**-1, aliases=("linear_mass_density",))

LINEAR_MOMENTUM = add_derived(M * L * T**-1, aliases=("linear_momentum",))

LUMINANCE = add_derived(J * L**-2, aliases=("luminance",))

LUMINOUS_FLUX = add_derived(J, aliases=("luminous_flux",))

# endregion // L

# region // M

MAGNETIC_FIELD = add_derived(A * L**-1, aliases=("magnetic_field",))

MAGNETIC_FLUX = add_derived(M * L**2 * T**-2 * A**-1, aliases=("magnetic_flux",))

MAGNETIC_INDUCTION_FIELD_STRENGTH = add_derived(M * T**-2 * A**-1, aliases=("magnetic_induction_field_strength",))

MAGNETIC_MOMENT = add_derived(L**2 * A, aliases=("magnetic_moment",))

MAGNETIC_PERMEABILITY = add_derived(M * L**2 * T**-2 * A**-2, aliases=("magnetic_permeability",))

MAGNETOMOTIVE_FORCE = add_derived(A, aliases=("magnetomotive_force",))

MASS = add_derived(M, aliases=("mass",))

MASS_DENSITY = add_derived(M * L**-3, aliases=("mass_density",))

MASS_FLOW_RATE = add_derived(M * T**-1, aliases=("mass_flow_rate",))

MASS_FLUX = add_derived(M * L**-2 * T**-1, aliases=("mass_flux",))

MASS_FRACTION = add_derived(D, aliases=("mass_fraction",))

MASS_TRANSFER_COEFFICIENT = add_derived(M * L**-2 * T**-1, aliases=("mass_transfer_coefficient",))

MOLALITY_OF_SOLUTE = add_derived(N * M**-1, aliases=("molality_of_solute",))

MOLAR_CONCENTRATION_MASS = add_derived(N, aliases=("molar_concentration_mass",))

MOLAR_FLOW_RATE = add_derived(N * T**-1, aliases=("molar_flow_rate",))

MOLAR_FLUX = add_derived(N * L**-2 * T**-1, aliases=("molar_flux",))

MOLAR_HEAT_CAPACITY = add_derived(L**2 * N**-1 * T**-2 * Θ**-1, aliases=("molar_heat_capacity",))

MOLARITY = add_derived(N * L**-3, aliases=("molarity",))

MOLE_FRACTION = add_derived(D, aliases=("mole_fraction",))

MOMENT_OF_INERTIA = add_derived(M * L**2, aliases=("moment_of_inertia",))

MOMENTUM_FLOW_RATE = add_derived(M * L * T**-2, aliases=("momentum_flow_rate",))

MOMENTUM_FLUX = add_derived(M * L**-1 * T**-2, aliases=("momentum_flux",))

# endregion // M

# region // N

NORMALITY_OF_SOLUTION = add_derived(N * L**-3, aliases=("normality_of_solution",))

# endregion // N

# region // O

# endregion // O

# region // P

PARTICLE_DENSITY = add_derived(M * L**-3, aliases=("particle_density",))

PERMEABILITY = add_derived(L**2, aliases=("permeability",))

PHOTON_EMISSION_RATE = add_derived(L**-2 * T**-1, aliases=("photon_emission_rate",))

POWER_PER_UNIT_MASS = add_derived(L**2 * T**-3, aliases=("power_per_unit_mass", "SPECIFIC_POWER", "specific_power"))

POWER_PER_UNIT_VOLUME = add_derived(M * L**-1 * T**-3, aliases=("power_per_unit_volume", "POWER_DENSITY", "power_density"))

POWER_THERMAL = add_derived(M * L**2 * T**-3, aliases=("power_thermal",))

PRESSURE = add_derived(M * L**-1 * T**-2, aliases=("pressure",))

# endregion // P

# region // Q

# endregion // Q

# region // R

RADIATION_DOSE_EQUIVALENT = add_derived(L**2 * T**-2, aliases=("radiation_dose_equivalent",))
RADIATION_EXPOSURE = add_derived(A * T * M**-2, aliases=("radiation_exposure",))

RADIOACTIVITY = add_derived(T**-1, aliases=("radioactivity",))

# endregion // R

# region // S

SECOND_MOMENT_OF_AREA = add_derived(L**4, aliases=("second_moment_of_area",))

SECOND_RADIATION_CONSTANT = add_derived(L * Θ, aliases=("second_radiation_constant", "PLANCK_CONSTANT", "planck_constant"))

SPECIFIC_ENTHALPY = add_derived(L**2 * T**-2, aliases=("specific_enthalpy",))

SPECIFIC_HEAT_CAPACITY_CONSTANT_PRESSURE = add_derived(L**2 * M * T**-2 * Θ**-1, aliases=("specific_heat_capacity",))

SPECIFIC_LENGTH = add_derived(L * M**-1, aliases=("specific_length",))

SPECIFIC_SURFACE = add_derived(L**2 * M**-1, aliases=("specific_surface",))

SPECIFIC_VOLUME = add_derived(L**3 * M**-1, aliases=("specific_volume",))

STRESS = add_derived(M * L**-1 * T**-2, aliases=("stress",))

SURFACE_MASS_DENSITY = add_derived(M * L**-2, aliases=("surface_mass_density",))

SURFACE_TENSION = add_derived(M * T**-2, aliases=("surface_tension",))

# endregion // S

# region // T

TEMPERATURE = add_derived(Θ, aliases=("temperature",))

THERMAL_CONDUCTIVITY = add_derived(M * L * T**-3 * Θ, aliases=("thermal_conductivity",))

TIME = add_derived(T, aliases=("time",))

TORQUE = add_derived(M * L**2 * T**-2, aliases=("torque",))

TURBULENCE_ENERGY_DISSIPATION_RATE = add_derived(L**2 * T**-3, aliases=("turbulence_energy_dissipation_rate",))

# endregion // T

# region // U

# endregion // U

# region // V

VELOCITY_ANGULAR = add_derived(T**-1, aliases=("velocity_angular",))

VELOCITY_LINEAR = add_derived(L * T**-1, aliases=("velocity_linear",))

VISCOSITY_DYNAMIC = add_derived(M * L**-1 * T**-1, aliases=("ViscosityDynamic",))

VISCOSITY_KINEMATIC = add_derived(L**2 * T**-1, aliases=("ViscosityKinematic",))

VOLUME = add_derived(L**3, aliases=("volume",))

VOLUME_FRACTION = add_derived(D, aliases=("volume_fraction",))

VOLUMETRIC_CALORIFIC_HEATING_VALUE = add_derived(M * L**-1 * T**-2, aliases=("volumetric_calorific_heat_capacity",))

VOLUMETRIC_COEFFICIENT_OF_THERMAL_EXPANSION = add_derived(M * L**-3 * Θ**-1, aliases=("volumetric_coefficient_of_thermal_expansion",))

VOLUMETRIC_FLOW_RATE = add_derived(L**3 * T**-1, aliases=("volumetric_flow_rate",))

VOLUMETRIC_FLUX = add_derived(L * T**-1, aliases=("volumetric_flux",))

VOLUMETRIC_MASS_FLOW_RATE = add_derived(M * L**-3 * T**-1, aliases=("volumetric_mass_flow_rate",))

# endregion // V

# region // W

WAVENUMBER = add_derived(L**-1, aliases=("wavenumber",))

# endregion // W


__all__ = ["dim"]
