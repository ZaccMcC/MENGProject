import json
import logging

import numpy as np

class Config:
    def __init__(self, file_path="config.json"):
        with open(file_path, "r") as f:
            data = json.load(f)

        # Store parameters in instance variables
        self.planes = data["planes"]
        self.sensor_area = data["sensor_area"]
        self.arc_movement = data["arc_movement"]
        self.simulation = data["simulation"]
        self.intersection = data["intersection"]
        self.visualization = data["visualization"]
        self.debugging = data["debugging"]
        self.performance = data["performance"]

        log_level = self.debugging.get("logging_level", "INFO").upper()
        logging.basicConfig(level=getattr(logging, log_level, logging.INFO))
        logging.info(f"Logging level set to {log_level}")


# Initialize config globally
config = Config()