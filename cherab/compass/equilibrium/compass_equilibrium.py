from raysect.core import Point2D

from cherab.tools.equilibrium import EFITEquilibrium

import numpy as np

class COMPASSEquilibrium:

    def __init__(self, data = None):
        if data is not None:
            self.data = data

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        self.verify_data_content(data)
        self._data = data

    @staticmethod
    def verify_data_content(data):
        """
        Dataset containing equilibrium data has to contain specific data variables and coordinates
        :param data: Dataset containing equilibrium data
        :return:
        """
        man_coords = ["time", "R", "Z"]  # mandatory coordinates in data dataset
        man_datavars = ["psi_grid", "psi_lcfs", "R_magnetic_axis", "Z_magnetic_axis",
                        "R_strike_point", "Z_strike_point", "psi_n", "Btor_vacuum_radius",
                        "R_lcfs", "Z_lcfs"]  # mandatory data variables in data dataset

        for i in man_coords:
            if not i in data.coords.keys():
                raise KeyError("Dataset data does not include mandatory coordinate {}.".format(i))

        for i in man_datavars:
            if not i in data.data_vars.keys():
                raise KeyError("Dataset data does not include mandatory data variable {}.".format(i))

    @staticmethod
    def process_efit_polygon(poly_r, poly_z):
        """
        Processes polygon data to match EFITEquilibrium requirements
        :param poly_r: Array with r polygon coordinated.
        :param poly_z: Array with z polygon coordinated.
        :return: polygon
        """

        if poly_r.shape != poly_z.shape:
            raise ValueError("EFIT polygon coordinate arrays are inconsistent in length.")

        n = poly_r.shape[0]
        if n < 2:
            raise ValueError("EFIT polygon coordinate contain less than 2 points.")

        # boundary polygon contains redundant points that must be removed
        unique = (poly_r != poly_r[0]) | (poly_z != poly_z[0])
        unique[0] = True  # first point must be included!
        poly_r = poly_r[unique]
        poly_z = poly_z[unique]

        # generate single array containing coordinates
        poly_coords = np.zeros((2, len(poly_r)))
        poly_coords[0, :] = poly_r
        poly_coords[1, :] = poly_z

        return poly_coords

    def time_slice(self, time):
        """
        Constructs the EFITEquilibrium object for the closes available time to the passed time
        :param time: Time to generate EFITEquilibrium object. The nearest available time slice is chosen
        :return: EFITEquilibrium object
        """

        time_slice = self._data.sel(time=time, method="nearest")

        r = time_slice.R.values
        z = time_slice.Z.values
        psi_grid = time_slice.psi_grid.values
        psi_axis = time_slice.psi_axis.values
        psi_lcfs = time_slice.psi_lcfs.values
        magnetic_axis = Point2D(time_slice.R_magnetic_axis.values, time_slice.Z_magnetic_axis.values)

        x_points = []
        for i, v in enumerate(zip(time_slice.R_xpoint.values, time_slice.Z_xpoint.values)):
            if not np.isnan(v[0]) and not np.isnan(v[1]):
                x_points.append(Point2D(v[0], v[1]))


        strike_points = []
        for i, v in enumerate(zip(time_slice.R_strike_point.values, time_slice.Z_strike_point.values)):
            if not np.isnan(v[0]) and not np.isnan(v[1]):
                strike_points.append(Point2D(v[0], v[1]))

        psi_n = time_slice.psi_n.values

        f_profile = np.concatenate((psi_n[np.newaxis, :], time_slice.f_profile.values[np.newaxis, :]))
        q_profile = np.concatenate((psi_n[np.newaxis, :], time_slice.q_profile.values[np.newaxis, :]))

        b_vacuum_radius = time_slice.Btor_vacuum_radius
        b_vacuum_magnitude = time_slice.Btor_vacuum_magnitude.values

        lcfs_polygon = self.process_efit_polygon(time_slice.R_lcfs.values, time_slice.Z_lcfs.values)

        if "R_limiter" in time_slice.data_vars.keys() and "Z_limiter":
            limiter_polygon = self.process_efit_polygon(time_slice.R_limiter.values, time_slice.Z_limiter.values)


        return EFITEquilibrium(r=r, z=z, psi_grid=psi_grid, psi_axis=psi_axis,psi_lcfs=psi_lcfs, magnetic_axis=magnetic_axis,
                                      x_points=x_points, strike_points=strike_points, f_profile=f_profile, q_profile=q_profile,
                                      b_vacuum_radius=b_vacuum_radius, b_vacuum_magnitude=b_vacuum_magnitude,
                                      lcfs_polygon=lcfs_polygon, limiter_polygon=limiter_polygon,
                                      time=time)
