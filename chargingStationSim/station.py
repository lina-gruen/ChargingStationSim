# -*- encoding: utf-8 -*-
"""
This file contains the Station class
"""

__author__ = 'Lina Grünbeck / lina.grunbeck@gmail.com'

from chargingStationSim.battery import Battery
from chargingStationSim.charger import Charger
from chargingStationSim.vehicle import Vehicle

class Station:
    """
    Class for a charging station.
    """

    vehicle_params = {'weight_class': None, 'dist_type': None, 'capacity': 150, 'efficiency': 5,
                      'drive_dist': 10, 'soc': 100}

    def __init__(self):
        """

        """
        self.batteries = []
        self.chargers = []
        self.vehicles = []

    def add_battery(self, capacity=150, soc=100):
        """
        Add a battery pack to the station.
        """
        self.batteries = self.batteries.append(Battery(capacity, soc))

    def add_charger(self):
        """
        Add a charger to the station.
        """
        self.chargers = self.chargers.append(Charger())

    def add_vehicle(self, vehicle_params):
        """
        Add a vehicle to the station.
        """
        self.vehicles = self.vehicles.append(Vehicle(vehicle_params))

    def


if __name__ == '__main__':
