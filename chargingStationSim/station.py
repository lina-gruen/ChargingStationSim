# -*- encoding: utf-8 -*-
"""
This file contains the Station class
"""

__author__ = 'Lina Grünbeck / lina.grunbeck@gmail.com'

from chargingStationSim.battery import Battery
from chargingStationSim.charger import Charger
from chargingStationSim.vehicle import Vehicle
from mesa import Model
# from mesa.time import BaseScheduler
from mesa.time import StagedActivation
from mesa.datacollection import DataCollector
# import random
# random.seed(1234)


class Station(Model):
    """
    Class for a charging station.
    """

    vehicle_params = {'weight': None, 'dist_type': None, 'capacity': 150, 'efficiency': 1.5, 'max_charge': 350}

    def __init__(self, num_vehicle, num_battery, num_charger, time_step):
        super().__init__()

        # Simulation-----------------------------------------------------------------

        # Make a scheduler that splits each iteration into two steps
        vehicle_steps = ['step_1', 'step_2']
        self.schedule = StagedActivation(model=self, stage_list=vehicle_steps,
                                         shuffle=False, shuffle_between_stages=False)
        # Variable to stop simulation if set to False.
        self.running = True
        # Time that passes for each step in hours.
        self.time_step = time_step
        # Duration for a simulation.
        # self.sim_time = sim_time
        # If the power of the chargers on the station have been updated. Should happen once for each step.
        self.power_updated = False

        # ---------------------------------------------------------------------------

        for num in range(num_vehicle):
            obj = Vehicle(unique_id=num, station=self, params=self.vehicle_params)
            self.schedule.add(obj)

        for num in range(num_battery):
            obj = Battery(unique_id=num_vehicle + num, station=self, capacity=150, soc=100)
            self.schedule.add(obj)

        # List to contain all chargers at the station.
        self.charge_list = [Charger(power=350, num_sockets=4) for _ in range(num_charger)]

        # Data collector for model and agent variables.
        self.datacollector = DataCollector(
            model_reporters={'Power': self.get_station_power}, agent_reporters={'Soc': 'soc', 'Arrival': 'arrival'}
        )

    def get_station_power(self):
        """
        Finds the power used for all chargers to return the total power used at the station.

        Returns
        -------

        """
        power_sum = [charger.used_power for charger in self.charge_list]
        return sum(power_sum)

    def step(self):
        """
        Actions to execute for each iteration of a simulation.
        """
        self.datacollector.collect(self)
        # Iterate through all agents (vehicles, batteries) in the model.
        self.schedule.step()
        # Reset variable for the next step. Checks if the power of the chargers is updated.
        self.power_updated = False


if __name__ == '__main__':
    pass
