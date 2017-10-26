
# Core and external imports
import numpy as np
from scipy.constants import electron_mass, atomic_mass
from raysect.core import Vector3D, translate
from raysect.primitive import Cylinder

# Cherab and raysect imports
from cherab.core import Species, Plasma, Maxwellian
from cherab.core.atomic import carbon
from cherab.core.math import Interpolate1DCubic, Interpolate2DCubic, IsoMapper3D, AxisymmetricMapper, Constant3D, Blend3D


def load_core_plasma_from_files(world, atomic_data, psirz_file, psin_file, electron_file, carbon_file):

    # Load equilibrium psi function
    loaded = np.loadtxt(psirz_file, delimiter="\t", skiprows=1)
    psi_R = loaded[:, 0]
    psi_Z = loaded[:, 1]
    psi_map = np.loadtxt(psin_file, delimiter="\t", skiprows=1)
    psin_2d = Interpolate2DCubic(psi_R, psi_Z, psi_map, extrapolate=True)
    psin_3d = AxisymmetricMapper(psin_2d)

    # Load electron species
    loaded = np.loadtxt(electron_file, delimiter="\t", skiprows=1)
    psi_coord = loaded[:, 0]
    electrons_temperature_axis = loaded[:, 1]
    electrons_densiy_axis = loaded[:, 2]

    flow_velocity = lambda x, y, z: Vector3D(0, 0, 0)  # Ignoring velocity, necessary but not used for this model.

    electorn_temperature_vs_psi = Interpolate1DCubic(psi_coord, electrons_temperature_axis, extrapolate=True)
    electron_temperature = Blend3D(Constant3D(0.0), IsoMapper3D(psin_3d, electorn_temperature_vs_psi), _inside_lcfs)
    electron_density_vs_psi = Interpolate1DCubic(psi_coord, electrons_densiy_axis, extrapolate=True)
    electron_density = Blend3D(Constant3D(0.0), IsoMapper3D(psin_3d, electron_density_vs_psi), _inside_lcfs)
    electron_distribution = Maxwellian(electron_density, electron_temperature, flow_velocity, electron_mass)

    # Load carbon species
    c_abundance_data = np.loadtxt(carbon_file, delimiter="\t", skiprows=1)

    c0_density_psi = Interpolate1DCubic(psi_coord, c_abundance_data[:, 0], extrapolate=True)
    c0_density = Blend3D(Constant3D(0.0), IsoMapper3D(psin_3d, c0_density_psi), _inside_lcfs)
    c0_distribution = Maxwellian(c0_density, electron_temperature, flow_velocity, carbon.atomic_weight * atomic_mass)
    c0_species = Species(carbon, 0, c0_distribution)

    c1_density_psi = Interpolate1DCubic(psi_coord, c_abundance_data[:, 1], extrapolate=True)
    c1_density = Blend3D(Constant3D(0.0), IsoMapper3D(psin_3d, c1_density_psi), _inside_lcfs)
    c1_distribution = Maxwellian(c1_density, electron_temperature, flow_velocity, carbon.atomic_weight * atomic_mass)
    c1_species = Species(carbon, 1, c1_distribution)

    c2_density_psi = Interpolate1DCubic(psi_coord, c_abundance_data[:, 2], extrapolate=True)
    c2_density = Blend3D(Constant3D(0.0), IsoMapper3D(psin_3d, c2_density_psi), _inside_lcfs)
    c2_distribution = Maxwellian(c2_density, electron_temperature, flow_velocity, carbon.atomic_weight * atomic_mass)
    c2_species = Species(carbon, 2, c2_distribution)

    c3_density_psi = Interpolate1DCubic(psi_coord, c_abundance_data[:, 3], extrapolate=True)
    c3_density = Blend3D(Constant3D(0.0), IsoMapper3D(psin_3d, c3_density_psi), _inside_lcfs)
    c3_distribution = Maxwellian(c3_density, electron_temperature, flow_velocity, carbon.atomic_weight * atomic_mass)
    c3_species = Species(carbon, 3, c3_distribution)

    c4_density_psi = Interpolate1DCubic(psi_coord, c_abundance_data[:, 4], extrapolate=True)
    c4_density = Blend3D(Constant3D(0.0), IsoMapper3D(psin_3d, c4_density_psi), _inside_lcfs)
    c4_distribution = Maxwellian(c4_density, electron_temperature, flow_velocity, carbon.atomic_weight * atomic_mass)
    c4_species = Species(carbon, 4, c4_distribution)

    c5_density_psi = Interpolate1DCubic(psi_coord, c_abundance_data[:, 5], extrapolate=True)
    c5_density = Blend3D(Constant3D(0.0), IsoMapper3D(psin_3d, c5_density_psi), _inside_lcfs)
    c5_distribution = Maxwellian(c5_density, electron_temperature, flow_velocity, carbon.atomic_weight * atomic_mass)
    c5_species = Species(carbon, 5, c5_distribution)

    c6_density_psi = Interpolate1DCubic(psi_coord, c_abundance_data[:, 6], extrapolate=True)
    c6_density = Blend3D(Constant3D(0.0), IsoMapper3D(psin_3d, c6_density_psi), _inside_lcfs)
    c6_distribution = Maxwellian(c6_density, electron_temperature, flow_velocity, carbon.atomic_weight * atomic_mass)
    c6_species = Species(carbon, 6, c6_distribution)

    # Assemble the plasma object
    plasma = Plasma(world)
    plasma.atomic_data = atomic_data
    plasma.electron_distribution = electron_distribution
    plasma.composition = [c0_species, c1_species, c2_species, c3_species, c4_species, c5_species, c6_species]
    plasma.b_field = lambda x, y, z: Vector3D(0, 0, 0.)  # ignoring magnetic field, necessary but not used for this model.

    # Give the plasma some information about COMPASS' cylindrical geometry
    plasma.geometry = Cylinder(1.0, 1.0)
    plasma.geometry_transform = translate(0, 0, -0.5)

    return plasma


# Criteria for being inside the plasma
def _inside_lcfs(x, y, z):
    if np.sqrt(x**2 + y**2) < 0.35 or np.sqrt(x**2 + y**2) > 0.75:
        return 0
    else:
        return 1.0

