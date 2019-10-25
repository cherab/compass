from cherab.compass.equilibrium.equilibrium_base import COMPASSEquilibrium_base
import cdb_extras.xarray_support as cdbxr
from pyCDB import client
cdb = client.CDBClient(host="cudb.tok.ipp.cas.cz",data_root="/compass/
CC19_COMPASS-U_data/")
#class COMPASSUpgradeEquilibrium(COMPASSEquilibrium_base):

#    def from_cdb(self, shot_number):

shot_number = 6400

shot = cudbxr.Shot(shot_number)
shot["Bphi/Fiesta_OUT"]