from cherab.compass.equilibrium.equilibrium_base import COMPASSEquilibrium_base
import xarray as xr
import numpy as np


class COMPASSUpgradeEquilibrium(COMPASSEquilibrium_base):

    def __init__(self):
        super().__init__()

    @classmethod
    def from_database(cls, shot_number):
        """
        Obtains EFIT equilibrium data from CDB database for the specified shot.
        :param shot_number: COMPASS shot number
        :return: COMPASSEquilibrium class
        """
        #set of imports of packages local to COMPASS-site done inside this function to maintain functionality
        #off-site
        import cdb_extras.xarray_support as cdbxr
        from pyCDB import client

        cudb = client.CDBClient(host="cudb.tok.ipp.cas.cz", data_root="/compass/CC19_COMPASS-U_data/")
        cdbxr.access_wrappers._global_CDBClient = cudb

        shot = cdbxr.Shot(shot_number)
        equilibrium = cls()

        equilibrium._data = shot["psi/fiesta_out"].copy()
        equilibrium._data.name = "psi_grid"
        equilibrium._data = equilibrium._data.to_dataset()
        equilibrium._data = equilibrium._data.rename({"fiesta_r": "R",
                                                      "fiesta_z": "Z"})

        equilibrium._data = equilibrium._data.merge(shot["psi_0/fiesta_out"].to_dataset())
        equilibrium._data = equilibrium._data.rename({"psi_0": "psi_axis"})

        equilibrium._data = equilibrium._data.merge(shot["psi_boundary/fiesta_out"].to_dataset())
        equilibrium._data = equilibrium._data.rename({"psi_boundary": "psi_lcfs"})

        equilibrium._data = equilibrium._data.merge(shot["r_mag/fiesta_out"].to_dataset())
        equilibrium._data = equilibrium._data.rename({"r_mag": "R_magnetic_axis"})

        equilibrium._data = equilibrium._data.merge(shot["z_mag/fiesta_out"].to_dataset())
        equilibrium._data = equilibrium._data.rename({"z_mag": "Z_magnetic_axis"})

        #add xpoint data
        tmp = shot["xp_lower_r/fiesta_out"].expand_dims({"xpoint": 1})
        tmp = xr.concat((tmp, shot["xp_upper_r/fiesta_out"].expand_dims({"xpoint": 1})), dim="xpoint")
        tmp.name = "R_xpoint"
        tmp = tmp.to_dataset()
        equilibrium._data = xr.merge((equilibrium._data, tmp))

        tmp = shot["xp_lower_z/fiesta_out"].expand_dims({"xpoint": 1})
        tmp = xr.concat((tmp, shot["xp_upper_z/fiesta_out"].expand_dims({"xpoint": 1})), dim="xpoint")
        tmp.name = "Z_xpoint"
        tmp = tmp.to_dataset()
        equilibrium._data = xr.merge((equilibrium._data, tmp))

        tmp = shot["sp_hfs_r/fiesta_out"].expand_dims({"strike_point": 1})
        tmp = xr.concat((tmp, shot["sp_hfs_r/fiesta_out"].expand_dims({"strike_point": 1})), dim="strike_point")
        tmp.name = "R_strike_point"
        tmp = tmp.to_dataset()
        equilibrium._data = xr.merge((equilibrium._data, tmp))

        tmp = shot["sp_hfs_z/fiesta_out"].expand_dims({"strike_point": 1})
        tmp = xr.concat((tmp, shot["sp_hfs_z/fiesta_out"].expand_dims({"strike_point": 1})), dim="strike_point")
        tmp.name = "Z_strike_point"
        tmp = tmp.to_dataset()


        equilibrium._data = xr.merge((equilibrium._data, tmp))

        equilibrium._data = equilibrium._data.merge(shot["f/fiesta_out"].to_dataset())
        equilibrium._data = equilibrium._data.rename({"f": "f_profile"})

        equilibrium._data = equilibrium._data.merge(shot["q/fiesta_out"].to_dataset())
        equilibrium._data = equilibrium._data.rename({"q": "q_profile"})

        equilibrium._data = equilibrium._data.merge(shot["Bt_vac_mag_axis/fiesta_out"].to_dataset())
        equilibrium._data = equilibrium._data.rename({"Bt_vac_mag_axis": "Btor_vacuum_magnitude"})

        equilibrium._data = equilibrium._data.merge(shot["Bt_vac_mag_axis/fiesta_out"].to_dataset())
        equilibrium._data = equilibrium._data.rename({"Bt_vac_mag_axis": "Btor_vacuum_radius"})


        r_boundary_signal = cudb.get_signal("boundary_r/fiesta_out:{0}".format(shot_number))
        z_boundary_signal = cudb.get_signal("boundary_z/fiesta_out:{0}".format(shot_number))

        boundary = xr.Dataset({"R_lcfs": (("time", "lcfs_vertex"), r_boundary_signal.data.T),
                               "Z_lcfs": (("time", "lcfs_vertex"), z_boundary_signal.data.T)},
                              coords={"time": r_boundary_signal.time_axis.data})

        equilibrium._data = xr.merge((equilibrium._data, boundary))

        tmp =shot["Z_limiter/fiesta_out"]
        tmp = xr.Dataset({"Z_limiter": ("limiter_vertex", tmp.Z_limiter.values)})
        equilibrium._data = equilibrium._data.merge(tmp)

        tmp =shot["R_limiter/fiesta_out"]
        tmp = xr.Dataset({"R_limiter": ("limiter_vertex", tmp.R_limiter.values)})
        equilibrium._data = equilibrium._data.merge(tmp)

        equilibrium._data = equilibrium._data.rename({"fiesta_psi_norm": "psi_n"})

        return equilibrium

if __name__ == "__main__":
    from cherab.tools.equilibrium.plot import plot_equilibrium
    eq_shot = COMPASSUpgradeEquilibrium.from_database(7400)
    time = 2.100

    time_slice = eq_shot.time_slice(time)
    plot_equilibrium(time_slice, detail=True)






