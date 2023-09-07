from cherab.compass.equilibrium.compass_equilibrium import COMPASSEquilibrium

import xarray as xr

def efit_from_cdb(shot_number):
    """
    Obtains EFIT equilibrium data from CDB database for the specified shot.
    :param shot_number: COMPASS shot number
    :return: COMPASSEquilibrium class
    """

    # imports of compass cudb specific inside function to confine dependency
    import cdb_extras.xarray_support as cdbxr

    shot = cdbxr.Shot(shot_number)

    data = shot["psi_RZ/EFIT"].copy()
    data.name = "psi_grid"
    data = data.to_dataset()

    data = data.merge(shot["psi_mag_axis/EFIT"].to_dataset())
    data = data.rename({"psi_mag_axis": "psi_axis"})

    data = data.merge(shot["psi_lcfs/EFIT"].to_dataset())

    data = data.merge(shot["RZ_mag_axis/EFIT"])
    data = data.rename({"R_mag_axis": "R_magnetic_axis", "Z_mag_axis": "Z_magnetic_axis"})

    data = data.merge(shot["RZ_xpoint/EFIT"])
    data = data.rename({"RZ_xpoint_axis1": "xpoint"})

    data = data.merge(shot["RZ_strike_points/EFIT"])
    data = data.rename({"RZ_strike_points_axis1": "strike_point",
                                                  "R_strike_points": "R_strike_point",
                                                  "Z_strike_points": "Z_strike_point"})

    data = data.merge(shot["RBphi/EFIT"].to_dataset())
    data = data.rename({"RBphi": "f_profile"})

    data = data.merge(shot["q/EFIT"].to_dataset())
    data = data.rename({"q": "q_profile"})

    data = data.merge(shot["B_vac_R_mag/EFIT"].to_dataset())
    data = data.rename({"B_vac_R_mag": "Btor_vacuum_magnitude"})

    data = data.merge(shot["R_mag_axis/EFIT"].to_dataset())
    data = data.rename({"R_mag_axis": "Btor_vacuum_radius"})

    data = data.merge(shot["RZ_bound/EFIT"])
    data = data.rename({"R_bound": "R_lcfs", "Z_bound": "Z_lcfs"})

    r_limiter = shot["R_limiter_input/EFIT"]
    r_limiter.name = "R_limiter"
    r_limiter = r_limiter.rename({"R_limiter_input_axis1": "limiter_vertex"})

    z_limiter = shot["Z_limiter_input/EFIT"]
    z_limiter.name = "Z_limiter"
    z_limiter = z_limiter.rename({"Z_limiter_input_axis1": "limiter_vertex"})

    limiter = xr.merge((r_limiter, z_limiter))
    data = data.merge(limiter)

    data = data.rename({"RZ_bound_axis1": "lcfs_vertex",
                                                  "R_axis1": "psi_grid_R_vertex",
                                                  "Z_axis2": "psi_grid_Z_vertex"})

    #initialise COMPASSEquilibrium
    equilibrium = COMPASSEquilibrium()
    equilibrium.shot_number = shot_number
    equilibrium._data = data

    return equilibrium
