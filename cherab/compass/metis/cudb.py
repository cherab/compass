from cherab.metis.data_source import MetisDataSource_base
import cdb_extras.xarray_support as cdbxr
from pyCDB import client
import numpy as np

class METISFromCUDB(MetisDataSource_base):

    def __init__(self, shot_number:int = None):
        super().__init__()

        self._cudb = client.CDBClient(host="cudb.tok.ipp.cas.cz", data_root="/compass/CC19_COMPASS-U_data/")
        cdbxr.access_wrappers._global_CDBClient = self._cudb
        self._metis_data_source_id = 2

        if shot_number is not None:
            self.shot_number = shot_number


    @property
    def shot_number(self):
        return self._shot_number

    @shot_number.setter
    def shot_number(self, value:int):
        self._shot_number = value
        self._shot = cdbxr.Shot(self._shot_number)

        self.get_data()

    def _get_data(self):
        metis_signals = self._cudb.query(
            "SELECT gs.generic_signal_name FROM generic_signals gs INNER JOIN data_signals ds USING(generic_signal_id) WHERE gs.data_source_id = {1} AND ds.record_number = {0}".format(
                int(self._shot_number), int(self._metis_data_source_id)))
        metis_output = self._cudb.query(
            "SELECT name FROM data_sources WHERE data_source_id = {0}".format(self._metis_data_source_id))

        zerod = {}
        profil0d = {}

        for i in metis_signals:
            if "profil0d" in i["generic_signal_name"]:
                key = i["generic_signal_name"].replace("profil0d_", "")
                signal_name = i["generic_signal_name"] + "/" + metis_output[0]["name"]
                try:
                    profil0d[key] = self._shot[signal_name].values.T
                except Exception:
                    pass

            elif "zerod" in i["generic_signal_name"]:
                key = i["generic_signal_name"].replace("zerod_", "")
                signal_name = i["generic_signal_name"] + "/" + metis_output[0]["name"]
                try:
                    zerod[key] = self._shot[signal_name].values
                except Exception:
                    pass

        profil0d["psin"] = np.divide((profil0d["psi"] - profil0d["psi"][0, :]),
                                     profil0d["psi"][-1, :] - profil0d["psi"][0, :])

        self._zerod_data = zerod
        self._profile0d_data = profil0d
