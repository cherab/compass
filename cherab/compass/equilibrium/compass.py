from cherab.compass.equilibrium.equilibrium_base import COMPASSEquilibrium_base

class COMPASSEquilibrium(COMPASSEquilibrium_base):

    @classmethod
    def from_cdb(cls, shot_number):
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
        equilibrium._data = equilibrium._data.rename({"psi_mag_axis":"psi_axis"})

        equilibrium._data = equilibrium._data.merge(shot["psi_lcfs/EFIT"].to_dataset())

        equilibrium._data = equilibrium._data.merge(shot["RZ_mag_axis/EFIT"])
        equilibrium._data = equilibrium._data.rename({"R_mag_axis": "R_magnetic_axis", "Z_mag_axis": "Z_magnetic_axis"})

        equilibrium._data = equilibrium._data.merge(shot["RZ_xpoint/EFIT"])


        equilibrium._data = equilibrium._data.merge(shot["RZ_strike_points/EFIT"])

        equilibrium._data = equilibrium._data.merge(shot["RBphi/EFIT"].to_dataset())
        equilibrium._data = equilibrium._data.rename({"RBphi": "f_profile"})

        equilibrium._data = equilibrium._data.merge(shot["q/EFIT"].to_dataset())
        equilibrium._data = equilibrium._data.rename({"q": "q_profile"})

        equilibrium._data = equilibrium._data.merge(shot["B_vac_R_geom/EFIT"].to_dataset())
        equilibrium._data = equilibrium._data.rename({"B_vac_R_geom": "b_vacuum_magnitude"})
        equilibrium._data.attrs["b_vacuum_radius"] = 0.56

        equilibrium._data = equilibrium._data.merge(shot["RZ_bound/EFIT"])
        equilibrium._data = equilibrium._data.rename({"R_bound": "R_lcfs", "Z_bound": "Z_lcfs" })

        equilibrium._data = equilibrium._data.merge(shot["R_limiter_input/EFIT"].to_dataset())
        equilibrium._data = equilibrium._data.merge(shot["Z_limiter_input/EFIT"].to_dataset())
        equilibrium._data = equilibrium._data.rename({"R_limiter_input": "R_limiter", "Z_limiter_input": "Z_limiter" })

        return equilibrium