"""Edit Settings Dialog"""

from json import loads

from PyQt6 import QtWidgets, uic

from not1mm.lib.ham_utility import gridtolatlon


class EditStation(QtWidgets.QDialog):
    """Edit Station Settings"""

    cty_file = {}

    def __init__(self, app_data_path):
        super().__init__(None)
        uic.loadUi(app_data_path / "settings.ui", self)
        self.buttonBox.clicked.connect(self.store)
        self.GridSquare.textEdited.connect(self.gridchanged)
        self.Call.textEdited.connect(self.call_changed)
        with open(
            app_data_path / "cty.json", "rt", encoding="utf-8"
        ) as file_descriptor:
            self.cty_file = loads(file_descriptor.read())

    def store(self):
        """dialog magic"""

    def gridchanged(self):
        """Populated the Lat and Lon fields when the gridsquare changes"""
        lat, lon = gridtolatlon(self.GridSquare.text())
        self.Latitude.setText(str(round(lat, 4)))
        self.Longitude.setText(str(round(lon, 4)))

    def call_changed(self):
        """Populate zones"""
        results = self.cty_lookup()
        if results is not None:
            result = results.get(next(iter(results)))
            self.CQZone.setText(str(result.get("cq", "")))
            self.ITUZone.setText(str(result.get("itu", "")))
            self.Country.setText(str(result.get("entity", "")))

    def cty_lookup(self):
        """Lookup callsign in cty.dat file"""
        callsign = self.Call.text()
        callsign = callsign.upper()
        for count in reversed(range(len(callsign))):
            searchitem = callsign[: count + 1]
            result = {
                key: val for key, val in self.cty_file.items() if key == searchitem
            }
            if not result:
                continue
            if result.get(searchitem).get("exact_match"):
                if searchitem == callsign:
                    return result
                continue
            return result
