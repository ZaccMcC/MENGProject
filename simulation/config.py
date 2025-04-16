import json
import logging

import numpy as np

class Config:
    def __init__(self, file_path=None, data=None):
        if data is not None:
            self.load_from_dict(data)
        elif file_path:
            with open(file_path, "r") as f:
                data = json.load(f)
            self.load_from_dict(data)
        else:
            raise ValueError("Must provide either file_path or data")

    def load_from_dict(self, data):
        self.planes = data["planes"]
        self.sensor_areas = data["sensor_areas"]
        self.aperture_areas = data["aperture_areas"]
        self.arc_movement = data["arc_movement"]
        self.simulation = data["simulation"]
        self.intersection = data["intersection"]
        self.visualization = data["visualization"]
        self.debugging = data["debugging"]
        self.performance = data["performance"]
        self.output = data["output"]

        log_level = self.debugging.get("logging_level", "INFO").upper()
        logging.basicConfig(level=getattr(logging, log_level, logging.INFO))

config = Config(file_path="../config.json")