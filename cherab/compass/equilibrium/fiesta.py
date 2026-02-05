from cherab.compass.equilibrium.compass_equilibrium import COMPASSEquilibrium
import xarray as xr


def fiesta_from_cudb(shot_number, revision=-1):
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

    data = shot[f"psi/fiesta_out:{shot_number}:{revision}"].copy()
    data.name = "psi_grid"
    data = data.to_dataset()
    data = data.rename({"fiesta_r": "R", "fiesta_z": "Z"})

    data = data.merge(shot[f"psi_0/fiesta_out:{shot_number}:{revision}"].to_dataset())
    data = data.rename({"psi_0": "psi_axis"})

    data = data.merge(shot[f"psi_boundary/fiesta_out:{shot_number}:{revision}"].to_dataset())
    data = data.rename({"psi_boundary": "psi_lcfs"})

    data = data.merge(shot[f"r_mag/fiesta_out:{shot_number}:{revision}"].to_dataset())
    data = data.rename({"r_mag": "R_magnetic_axis"})

    data = data.merge(shot[f"z_mag/fiesta_out:{shot_number}:{revision}"].to_dataset())
    data = data.rename({"z_mag": "Z_magnetic_axis"})

    # add xpoint data
    tmp = shot[f"xp_lower_r/fiesta_out:{shot_number}:{revision}"].expand_dims({"xpoint": 1})
    tmp = xr.concat((tmp, shot[f"xp_upper_r/fiesta_out:{shot_number}:{revision}"].expand_dims({"xpoint": 1})), dim="xpoint")
    tmp.name = "R_xpoint"
    tmp = tmp.to_dataset()
    data = xr.merge((data, tmp))

    tmp = shot[f"xp_lower_z/fiesta_out:{shot_number}:{revision}"].expand_dims({"xpoint": 1})
    tmp = xr.concat((tmp, shot[f"xp_upper_z/fiesta_out:{shot_number}:{revision}"].expand_dims({"xpoint": 1})), dim="xpoint")
    tmp.name = "Z_xpoint"
    tmp = tmp.to_dataset()
    data = xr.merge((data, tmp))

    tmp = shot[f"sp_hfs_r/fiesta_out:{shot_number}:{revision}"].expand_dims({"strike_point": 1})
    tmp = xr.concat((tmp, shot[f"sp_hfs_r/fiesta_out:{shot_number}:{revision}"].expand_dims({"strike_point": 1})), dim="strike_point")
    tmp.name = "R_strike_point"
    tmp = tmp.to_dataset()
    data = xr.merge((data, tmp))

    tmp = shot[f"sp_hfs_z/fiesta_out:{shot_number}:{revision}"].expand_dims({"strike_point": 1})
    tmp = xr.concat((tmp, shot[f"sp_hfs_z/fiesta_out:{shot_number}:{revision}"].expand_dims({"strike_point": 1})), dim="strike_point")
    tmp.name = "Z_strike_point"
    tmp = tmp.to_dataset()

    data = xr.merge((data, tmp))

    data = data.merge(shot[f"f/fiesta_out:{shot_number}:{revision}"].to_dataset())
    data = data.rename({"f": "f_profile"})

    data = data.merge(shot[f"q/fiesta_out:{shot_number}:{revision}"].to_dataset())
    data = data.rename({"q": "q_profile"})

    data = data.merge(shot[f"Bt_vac_mag_axis/fiesta_out:{shot_number}:{revision}"].to_dataset())
    data = data.rename({"Bt_vac_mag_axis": "Btor_vacuum_magnitude"})

    data = data.merge(shot[f"Bt_vac_mag_axis/fiesta_out:{shot_number}:{revision}"].to_dataset())
    data = data.rename({"Bt_vac_mag_axis": "Btor_vacuum_radius"})

    tmp = shot[f"boundary_closed_r/fiesta_out:{shot_number}:{revision}"].to_dataset().rename({"boundary_closed_r": "R_lcfs",
                                                                    "boundary_closed_r_axis1": "lcfs_vertex"})
    tmp = tmp.merge(shot[f"boundary_closed_z/fiesta_out:{shot_number}:{revision}"].to_dataset().rename({"boundary_closed_z": "Z_lcfs",
                                                                              "boundary_closed_z_axis1": "lcfs_vertex"}))
    data = data.merge(tmp)

    tmp = shot[f"Z_limiter/fiesta_out:{shot_number}:{revision}"]
    tmp = xr.Dataset({"Z_limiter": ("limiter_vertex", tmp.Z_limiter.values)})
    data = data.merge(tmp)

    tmp = shot[f"R_limiter/fiesta_out:{shot_number}:{revision}"]
    tmp = xr.Dataset({"R_limiter": ("limiter_vertex", tmp.R_limiter.values)})
    data = data.merge(tmp)

    data = data.rename({"fiesta_psi_norm": "psi_n"})

    equilibrium = COMPASSEquilibrium()
    equilibrium._data = data

    return equilibrium
