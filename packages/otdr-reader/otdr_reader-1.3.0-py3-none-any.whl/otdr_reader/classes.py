import re
from dataclasses import dataclass
from datetime import datetime
from typing import List

import numpy as np

import pyotdr


@dataclass
class Event:
    type: str
    x: float
    y: float


@dataclass
class Otdr:
    filename: str
    positions: List
    attenuations: List
    events: List[Event]

    def __init__(self, filename: str):
        self.filename = filename
        _, self._results, tracedata = pyotdr.read.sorparse(filename=filename)
        self.timestamp = datetime.fromtimestamp(
            int(self._results["FxdParams"]["date/time"][-15:-5])
        )
        self.pulse_width_ns = int(
            re.findall(r"\d+", self._results["FxdParams"]["pulse width"])[0]
        )
        self.wavelength = float(
            re.findall(r"\d+", self._results["FxdParams"]["wavelength"])[0]
        )
        self.refractive_index = float(
            re.findall(r"\d+\.\d+", self._results["FxdParams"]["index"])[0]
        )
        self.averaging_time_s = int(
            re.findall(r"\d+", self._results["FxdParams"]["averaging time"])[0]
        )
        self.positions = list()
        self.attenuations = list()
        for line in tracedata:
            position, attenuation = line.split("\t")
            self.positions.append(float(position))
            self.attenuations.append(float(attenuation))
        self.parse_events()

    def smooth(self, window: int = 10):
        cumsum_vec = np.cumsum(np.insert(self.attenuations, 0, 0))
        self.attenuations = (cumsum_vec[window:] - cumsum_vec[:-window]) / window

    def parse_events(self):
        self.events = list()
        for event in self._results["KeyEvents"].values():
            if isinstance(event, dict):
                try:
                    index_event = next(
                        x[0]
                        for x in enumerate(self.positions)
                        if x[1] > float(event["distance"])
                    )
                    self.events.append(
                        Event(
                            x=float(event["distance"]),
                            y=self.attenuations[index_event],
                            type=event["type"].split(" ")[-1],
                        )
                    )
                except KeyError:
                    pass
