import unittest

from cherab.compass.equilibrium import COMPASSEquilibrium

import xarray as xr

class TesFiestaEquilibria(unittest.TestCase):


    def test_mandatory_content(self):
        data = xr.Dataset()

        #leave out time coordinate

        with self.assertRaises(KeyError):
            COMPASSEquilibrium(data)


