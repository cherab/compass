from cherab.compass.equilibrium.equilibrium_base import COMPASSEquilibrium_base
import numpy as np
import xarray as xr

class COMPASSEquilibrium(COMPASSEquilibrium_base):

    def __init__(self):
        super().__init__()

    @classmethod
    def from_database(cls, shot_number):
        """
        Obtains EFIT equilibrium data from CDB database for the specified shot.
        :param shot_number: COMPASS shot number
        :return: COMPASSEquilibrium class
        """
        import cdb_extras.xarray_support as cdbxr #if we want to read equilibrium data from a file without cdb installed....

        shot = cdbxr.Shot(shot_number)

        equilibrium = cls()
        equilibrium.shot_number = shot_number


        equilibrium._data = shot["psi_RZ/EFIT"].copy()
        equilibrium._data.name = "psi_grid"
        equilibrium._data = equilibrium._data.to_dataset()

        equilibrium._data = equilibrium._data.merge(shot["psi_mag_axis/EFIT"].to_dataset())
        equilibrium._data = equilibrium._data.rename({"psi_mag_axis": "psi_axis"})

        equilibrium._data = equilibrium._data.merge(shot["psi_lcfs/EFIT"].to_dataset())

        equilibrium._data = equilibrium._data.merge(shot["RZ_mag_axis/EFIT"])
        equilibrium._data = equilibrium._data.rename({"R_mag_axis": "R_magnetic_axis", "Z_mag_axis": "Z_magnetic_axis"})

        equilibrium._data = equilibrium._data.merge(shot["RZ_xpoint/EFIT"])
        equilibrium._data = equilibrium._data.rename({"RZ_xpoint_axis1": "xpoint"})

        equilibrium._data = equilibrium._data.merge(shot["RZ_strike_points/EFIT"])
        equilibrium._data = equilibrium._data.rename({"RZ_strike_points_axis1": "strike_point",
                                                      "R_strike_points": "R_strike_point",
                                                      "Z_strike_points": "Z_strike_point"})

        equilibrium._data = equilibrium._data.merge(shot["RBphi/EFIT"].to_dataset())
        equilibrium._data = equilibrium._data.rename({"RBphi": "f_profile"})

        equilibrium._data = equilibrium._data.merge(shot["q/EFIT"].to_dataset())
        equilibrium._data = equilibrium._data.rename({"q": "q_profile"})

        equilibrium._data = equilibrium._data.merge(shot["B_vac_R_mag/EFIT"].to_dataset())
        equilibrium._data = equilibrium._data.rename({"B_vac_R_mag": "Btor_vacuum_magnitude"})

        equilibrium._data = equilibrium._data.merge(shot["R_mag_axis/EFIT"].to_dataset())
        equilibrium._data = equilibrium._data.rename({"R_mag_axis": "Btor_vacuum_radius"})

        equilibrium._data = equilibrium._data.merge(shot["RZ_bound/EFIT"])
        equilibrium._data = equilibrium._data.rename({"R_bound": "R_lcfs", "Z_bound": "Z_lcfs" })

        r_limiter = shot["R_limiter_input/EFIT"]
        r_limiter.name = "R_limiter"
        r_limiter = r_limiter.rename({"R_limiter_input_axis1":"limiter_vertex"})


        z_limiter = shot["Z_limiter_input/EFIT"]
        z_limiter.name = "Z_limiter"
        z_limiter = z_limiter.rename({"Z_limiter_input_axis1": "limiter_vertex"})

        limiter = xr.merge((r_limiter, z_limiter))
        equilibrium._data = equilibrium._data.merge(limiter)

        equilibrium._data = equilibrium._data.rename({"RZ_bound_axis1": "lcfs_vertex",
                                      "R_axis1": "psi_grid_R_vertex",
                                      "Z_axis2":"psi_grid_Z_vertex"})

        return equilibrium



if __name__ == "__main__":
    eq_shot = COMPASSEquilibrium.from_database(15001)
    time = 1100

    eq = eq_shot.time_slice(time)

    import matplotlib.pyplot as plt
    time_slice = eq_shot.data.sel(time = 1100, method="nearest")

    sadf, ax = plt.subplots()
    ax.plot(time_slice.R_lcfs.values, time_slice.Z_lcfs.values)