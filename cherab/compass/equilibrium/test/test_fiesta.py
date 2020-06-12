import unittest
from cherab.compass.equilibrium.fiesta import fiesta_from_cudb

class TesFiestaEquilibria(unittest.TestCase):

    def test_fiesta_from_cudb(self):
        """Test initialisation of COMPASS EFIT equilibrium from cdb."""

        shot_number = 6400
        time = 1.5

        equilibrium = fiesta_from_cudb(shot_number)
        time_slice = equilibrium.time_slice(1.5)