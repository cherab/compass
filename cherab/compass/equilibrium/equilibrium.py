import h5py
import numpy as np
from raysect.core import Point2D
from cherab.tools.equilibrium import EFITEquilibrium

"""
COMPASS equilibrium data reading routines
"""


class COMPASSEquilibrium:

    """
    Loads COMPASS efit reconstruction. Either shot number or path has to be passed.
    If shot number is specified, path to the efit file is obtained via cdb and data
    is loaded. Otherwise path to the efit file has to be specified.

    :param shot_number: COMPASS shot number
    :param path: Path to the efit file
    :param revision:
    """
    def __init__(self, shot_number=None, path=None, revision=1):
        self.shot_number = shot_number

        if shot_number is None and path is None:
            raise ValueError("Equilibrium has to be specified by either shot number or a path to the efit file")

        if shot_number is not None:
            import pyCDB.client
            cdb = pyCDB.client.CDBClient()
            sig_ref = cdb.get_signal_references(record_number=shot_number,
                                        generic_signal_id=2860,
                                        revision=revision)[0]
            path = cdb.get_data_file_reference(**sig_ref)

        self.file_path = path

        self._read_efitfile(self.file_path)

    def _read_efitfile(self, path):
        with h5py.File(path, "r") as f:
            # read time coordinates
            self._time_slice = f["time"].value

            # read 2D poloidal flux map
            self._r = f["output/profiles2D/r"].value
            self._z = f["output/profiles2D/z"].value
            self._psi_grid = f["output/profiles2D/poloidalFlux"].value

            # read poloidal flux on axis and lcfs
            self._psi_axis = f["output/globalParameters/psiAxis"].value
            self._psi_lcfs = f["output/globalParameters/psiBoundary"].value

            # read positions of magnetic axis
            self._magnetic_axis_r = f["output/globalParameters/magneticAxisR"].value
            self._magnetic_axis_z = f["output/globalParameters/magneticAxisZ"].value

            # get vacuum toroidal field on axis
            self._b_vacuum_radius = 0.56
            self._b_vacuum_magnitude = f["output/globalParameters/bvacRgeom"].value

            # read last close flux surface contour points
            self._lcfs_r = f["output/separatrixGeometry/boundaryCoordsR"].value
            self._lcfs_z = f["output/separatrixGeometry/boundaryCoordsZ"].value

            # read limiter contour points
            self._limiter_r = f["input/limiter/rValues"].value
            self._limiter_z = f["input/limiter/zValues"].value

            #get equilibrium important points
            self._strikepoint_r = f["output/separatrixGeometry/strikepointCoordsR"].value
            self._strikepoint_z = f["output/separatrixGeometry/strikepointCoordsZ"].value

            self._xpoint_r = f["output/separatrixGeometry/xpointCoordsR"].value
            self._xpoint_z = f["output/separatrixGeometry/xpointCoordsZ"].value


            self._rBphi = f["output/fluxFunctionProfiles/rBphi"].value

            self._psin = f["output/fluxFunctionProfiles/normalizedPoloidalFlux"].value


    def time(self, time):
        """
        Returns an equilibrium object for the time-slice closest to the requested time.
        The specific time-slice returned is held in the time attribute of the returned object.
        :param time: The equilibrium time point.
        :returns: An EFITEquilibrium object.
        """
        time_index, time_slice = self._find_nearest(self._time_slice, time)

        r = self._r[time_index, :]  # get the R coords for psi_grid
        z = self._z[time_index, :]  # get the Z coords for psi_grid

        psi_grid = self._psi_grid[time_index, :, :]
        psi_axis = self._psi_axis[time_index]
        psi_lcfs = self._psi_lcfs[time_index]

        magnetic_axis = Point2D(self._magnetic_axis_r[time_index],
                                self._magnetic_axis_z[time_index])

        b_vacuum_radius = self._b_vacuum_radius
        b_vacuum_magnitude = self._b_vacuum_magnitude[time_index]

        lcfs_polygon = self._process_efit_polygon(self._lcfs_r[time_index, :],
                                                  self._lcfs_z[time_index, :])

        limiter_polygon = self._process_efit_polygon(self._limiter_r[time_index, :],
                                                     self._limiter_z[time_index, :])

        strikepoints = self._process_efit_points(self._strikepoint_r[time_index, :],
                                                 self._strikepoint_z[time_index, :])

        xpoints = self._process_efit_points(self._xpoint_r[time_index, :],
                                            self._xpoint_z[time_index, :])

        f_profile = np.array([self._psin, self._rBphi[time_index, :]])

        equilibrium = EFITEquilibrium(r=r, z=z, psi_grid=psi_grid, psi_axis=psi_axis,
                                      psi_lcfs=psi_lcfs, magnetic_axis=magnetic_axis,
                                      x_points = xpoints, strike_points=strikepoints,
                                      f_profile=f_profile, b_vacuum_radius=b_vacuum_radius,
                                      b_vacuum_magnitude=b_vacuum_magnitude,
                                      lcfs_polygon=lcfs_polygon, limiter_polygon=limiter_polygon,
                                      time=time_slice)

        return equilibrium

    def _process_efit_points(self, point_r, point_z):
        #avoid using the point if any coordinate is nan
        point_list = []
        for i in range(point_r.shape[0]):
            if not np.isnan(point_r[i]) and not np.isnan(point_z[i]):
                point_list.append(Point2D(point_r[i], point_z[i]))

        return point_list

    def _find_nearest(self, array, value):
        if array.min() > value or array.max() < value:
            raise IndexError("Requested value is outside the range of the data.")

        idx = np.argmin(np.abs(array - value))
        return idx, array[idx]

    def _process_efit_polygon(self, poly_r, poly_z):

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

if __name__ == "__main__":
    from os.path import expanduser
    from cherab.tools.equilibrium import plot_equilibrium
    path = expanduser("~/EFIT/17636.1.h5")

    equilibrium = COMPASSEquilibrium(path=path)
    eq_slice = equilibrium.time(1.135)
    plot_equilibrium(equilibrium=eq_slice, detail=True, resolution=0.01)