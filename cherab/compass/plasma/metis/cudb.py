from cherab.metis.data_source import MetisDataSource_base
from cherab.metis import METISModel

from pyCDB import client
import cdb_extras.xarray_support as cdbxr

import numpy as np


class METISFromCUDB(MetisDataSource_base):

    def __init__(self, shot_number: int = None):
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
    def shot_number(self, value: int):
        self._shot_number = value
        self._shot = cdbxr.Shot(self._shot_number)

        self.get_data()

    @property
    def profil0d_signals(self):
        return self._profil0d_signals

    @property
    def zerod_signals(self):
        return self._zerod_signals

    def update_signal_names(self, shot_number=None):
        if shot_number is None:
            shot_number = self._shot_number

        # get all generic signals belonging to the metis output data source and available for the given shot number
        metis_signals = self._cudb.query(
            "SELECT gs.generic_signal_name FROM generic_signals gs INNER JOIN data_signals ds USING(generic_signal_id) WHERE gs.data_source_id = {1} AND ds.record_number = {0}".format(
                int(self._shot_number), int(self._metis_data_source_id)))
        # get the metis output signal name
        metis_output = self._cudb.query(
            "SELECT name FROM data_sources WHERE data_source_id = {0}".format(self._metis_data_source_id))

        # get dictionariers with profile names as keys and signal names as items
        self._profil0d_signals = {}
        self._zerod_signals = {}
        for i in metis_signals:
            if "profil0d" in i["generic_signal_name"]:
                key = i["generic_signal_name"].replace("profil0d_", "")
                signal_name = i["generic_signal_name"] + "/" + metis_output[0]["name"]
                self._profil0d_signals[key] = signal_name
            elif "zerod" in i["generic_signal_name"]:
                key = i["generic_signal_name"].replace("zerod_", "")
                signal_name = i["generic_signal_name"] + "/" + metis_output[0]["name"]
                self._zerod_signals[key] = signal_name

    def _get_data(self):
        # update signal names just in case
        self.update_signal_names()

        zerod = {}
        profil0d = {}

        for key, item in self._profil0d_signals.items():
            try:
                profil0d[key] = self._shot[item].values.T
            except Exception:
                pass

        for key, item in self._zerod_signals.items():
            try:
                zerod[key] = self._shot[item].values
            except Exception:
                pass

        profil0d["psin"] = np.divide((profil0d["psi"] - profil0d["psi"][0, :]),
                                     profil0d["psi"][-1, :] - profil0d["psi"][0, :])

        self._zerod_data = zerod
        self._profile0d_data = profil0d

def metis_from_cudb(shot_number):
    return METISModel(METISFromCUDB(shot_number))
