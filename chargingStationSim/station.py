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
        self.batteries.append(Battery(capacity, soc))

    def add_charger(self):
        """
        Add a charger to the station.
        """
        self.chargers.append(Charger())

    def add_vehicle(self, vehicle_params=vehicle_params):
        """
        Add a vehicle to the station.
        """
        self.vehicles.append(Vehicle(vehicle_params))

    def charge(self):
        for vehicle in self.vehicles:
            for charger in self.chargers:
                if not charger.occupied:
                    vehicle.charge_vehicle()
                else:
                    pass


if __name__ == '__main__':
    station = Station()
    station.add_battery(150, 100)
    station.add_charger()
    station.add_vehicle()
    print(station.batteries[0].get_soc())
    station.batteries[0].discharge(50)
    print(station.batteries[0].get_soc())

