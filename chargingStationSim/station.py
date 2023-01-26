# -*- encoding: utf-8 -*-
"""
This file contains the Station class
"""

__author__ = 'Lina Grünbeck / lina.grunbeck@gmail.com'

from chargingStationSim.battery import Battery
from chargingStationSim.charger import Charger
from chargingStationSim.vehicle import Vehicle
from mesa import Model
from mesa.time import BaseScheduler


class Station(Model):
    """
    Class for a charging station.
    """

    vehicle_params = {'weight_class': None, 'dist_type': None, 'capacity': 150, 'efficiency': 5,
                      'drive_dist': 10}

    def __init__(self, num_vehicle, num_battery, num_charger):
        super().__init__()
        self.schedule = BaseScheduler(self)

        for num in range(num_vehicle):
            obj = Vehicle(num, self, self.vehicle_params, 10)
            self.schedule.add(obj)

        for num in range(num_battery):
            obj = Battery(num + num_vehicle, self, 150, 100)
            self.schedule.add(obj)

        # List to contain all chargers at the station.
        self.charge_list = [Charger(num) for num in range(num_charger)]

    def step(self):
        """
        Actions to execute for each iteration of a simulation.
        """
        # Iterate through all agents (vehicles, batteries) in the model.
        self.schedule.step()


if __name__ == '__main__':
    model = Station(6, 1, 4)
    model.step()

