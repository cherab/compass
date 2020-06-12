import unittest
from cherab.compass.equilibrium.efit import efit_from_cudb

class TesFiestaEquilibria(unittest.TestCase):

    def test_fiesta_from_cudb(self):
        """Test initialisation of fiesta data for COMPASS Upgrade from cudb."""

        shot_number = 15001
        time = 1.1

        equilibrium = efit_from_cudb(shot_number)
        time_slice = equilibrium.time_slice(1.5)
