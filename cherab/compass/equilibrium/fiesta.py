from cherab.compass.equilibrium.compass_equilibrium import COMPASSEquilibrium
import xarray as xr


def fiesta_from_cudb(shot_number):
    """
    Obtains Fiesta equilibrium for COMPASS Upgrade from the cudb database and returns a COMPASSEquilibrium object.
    :param shot_number: Shot number to load from cudb
    :return: COMPASSEquilibrium
    """

    # imports of compass cudb specific inside function to confine dependency
    import cdb_extras.xarray_support as cdbxr
    from pyCDB import client

    cudb = client.CDBClient(host="cudb.tok.ipp.cas.cz", data_root="/compass/CC19_COMPASS-U_data/")
    cdbxr.access_wrappers._global_CDBClient = cudb

    shot = cdbxr.Shot(shot_number)

    data = shot["psi/fiesta_out"].copy()
    data.name = "psi_grid"
    data = data.to_dataset()
    data = data.rename({"fiesta_r": "R", "fiesta_z": "Z"})

    data = data.merge(shot["psi_0/fiesta_out"].to_dataset())
    data = data.rename({"psi_0": "psi_axis"})

    data = data.merge(shot["psi_boundary/fiesta_out"].to_dataset())
    data = data.rename({"psi_boundary": "psi_lcfs"})

    data = data.merge(shot["r_mag/fiesta_out"].to_dataset())
    data = data.rename({"r_mag": "R_magnetic_axis"})

    data = data.merge(shot["z_mag/fiesta_out"].to_dataset())
    data = data.rename({"z_mag": "Z_magnetic_axis"})

    # add xpoint data
    tmp = shot["xp_lower_r/fiesta_out"].expand_dims({"xpoint": 1})
    tmp = xr.concat((tmp, shot["xp_upper_r/fiesta_out"].expand_dims({"xpoint": 1})), dim="xpoint")
    tmp.name = "R_xpoint"
    tmp = tmp.to_dataset()
    data = xr.merge((data, tmp))

    tmp = shot["xp_lower_z/fiesta_out"].expand_dims({"xpoint": 1})
    tmp = xr.concat((tmp, shot["xp_upper_z/fiesta_out"].expand_dims({"xpoint": 1})), dim="xpoint")
    tmp.name = "Z_xpoint"
    tmp = tmp.to_dataset()
    data = xr.merge((data, tmp))

    tmp = shot["sp_hfs_r/fiesta_out"].expand_dims({"strike_point": 1})
    tmp = xr.concat((tmp, shot["sp_hfs_r/fiesta_out"].expand_dims({"strike_point": 1})), dim="strike_point")
    tmp.name = "R_strike_point"
    tmp = tmp.to_dataset()
    data = xr.merge((data, tmp))

    tmp = shot["sp_hfs_z/fiesta_out"].expand_dims({"strike_point": 1})
    tmp = xr.concat((tmp, shot["sp_hfs_z/fiesta_out"].expand_dims({"strike_point": 1})), dim="strike_point")
    tmp.name = "Z_strike_point"
    tmp = tmp.to_dataset()

    data = xr.merge((data, tmp))

    data = data.merge(shot["f/fiesta_out"].to_dataset())
    data = data.rename({"f": "f_profile"})

    data = data.merge(shot["q/fiesta_out"].to_dataset())
    data = data.rename({"q": "q_profile"})

    data = data.merge(shot["Bt_vac_mag_axis/fiesta_out"].to_dataset())
    data = data.rename({"Bt_vac_mag_axis": "Btor_vacuum_magnitude"})

    data = data.merge(shot["Bt_vac_mag_axis/fiesta_out"].to_dataset())
    data = data.rename({"Bt_vac_mag_axis": "Btor_vacuum_radius"})

    tmp = shot["boundary_closed_r/fiesta_out"].to_dataset().rename({"boundary_closed_r": "R_lcfs",
                                                                    "boundary_closed_r_axis1": "lcfs_vertex"})
    tmp = tmp.merge(shot["boundary_closed_z/fiesta_out"].to_dataset().rename({"boundary_closed_z": "Z_lcfs",
                                                                              "boundary_closed_z_axis1": "lcfs_vertex"}))
    data = data.merge(tmp)

    tmp = shot["Z_limiter/fiesta_out"]
    tmp = xr.Dataset({"Z_limiter": ("limiter_vertex", tmp.Z_limiter.values)})
    data = data.merge(tmp)

    tmp = shot["R_limiter/fiesta_out"]
    tmp = xr.Dataset({"R_limiter": ("limiter_vertex", tmp.R_limiter.values)})
    data = data.merge(tmp)

    data = data.rename({"fiesta_psi_norm": "psi_n"})

    equilibrium = COMPASSEquilibrium()
    equilibrium._data = data

    return equilibrium
