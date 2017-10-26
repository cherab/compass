
import os
import matplotlib.pyplot as plt
plt.ion()
from raysect.optical import World
from raysect.core import translate, Vector3D, rotate_basis
from raysect.optical.observer import PinholeCamera
from raysect.optical.observer import RGBPipeline2D, PowerPipeline2D

from cherab.core.atomic import Line, carbon
from cherab.core.model import ExcitationLine, RecombinationLine
from cherab.openadas import OpenADAS
from cherab.compass import load_core_plasma_from_files


psirz_file = os.path.join(os.path.dirname(__file__), "data/psi_RZ.txt")
psin_file = os.path.join(os.path.dirname(__file__), "data/psi.txt")
electron_file = os.path.join(os.path.dirname(__file__), "data/electrons.txt")
carbon_file = os.path.join(os.path.dirname(__file__), "data/abunC.txt")


world = World()
adas = OpenADAS(permit_extrapolation=True)
plasma = load_core_plasma_from_files(world, adas, psirz_file, psin_file, electron_file, carbon_file)


ciii_465 = Line(carbon, 2, (11, 10))  # wavelength=465.01

plasma.models = [
    ExcitationLine(ciii_465)
]


cam = PinholeCamera((512, 512), parent=world, transform=translate(-2, 0, 0)*rotate_basis(Vector3D(1, 0, 0), Vector3D(0, 0, 1)))
cam.pixel_samples = 1
cam.observe()

cam = PinholeCamera((512, 512), parent=world, transform=translate(-1.2, 0.4, 0)*rotate_basis(Vector3D(1, 0, 0), Vector3D(0, 0, 1)))
cam.pixel_samples = 1
cam.observe()

