# -*- encoding: utf-8 -*-
"""
This file contains the Station class
"""

__author__ = 'Lina Grünbeck / lina.grunbeck@gmail.com'

from chargingStationSim.battery import Battery
from chargingStationSim.charger import Charger
from chargingStationSim.vehicle import Group1, Group2, Group3, Group4
from mesa import Model
# from mesa.time import BaseScheduler
from mesa.time import StagedActivation
from mesa.datacollection import DataCollector
import pandas as pd
# import random
# random.seed(1234)


class Station(Model):
    """
    Class for a charging station.
    """

    # Parameters for each vehicle group containing mean values to use in a probability distribution.
    vehicle_params = {'Group1': {'weight': None, 'capacity': (100, 150, 200), 'max_charge': (150, 200, 250)},
                      'Group2': {'weight': None, 'capacity': (100, 150, 200), 'max_charge': (150, 200, 250)},
                      'Group3': {'weight': None, 'capacity': (200, 250, 300), 'max_charge': (200, 250, 350)},
                      'Group4': {'weight': None, 'capacity': (250, 300, 350), 'max_charge': (350, 400, 450)}}

    def __init__(self, num_group1, num_group2, num_group3, num_group4, num_battery, num_charger,
                 station_limit, time_resolution, sim_time):
        """
        Parameters
        ----------
        num_group1 : int
        num_group2 : int
        num_group3 : int
        num_group4 : int
        num_battery: int
        num_charger: int
        limit: int
        time_resolution: int
        sim_time: int
        """
        super().__init__()

        # Station-------------------------------------------------------------------------------------------
        self.batt_power = 0

        # Simulation----------------------------------------------------------------------------------------

        # Make a scheduler that splits each iteration into two steps
        vehicle_steps = ['step_1', 'step_2']
        self.schedule = StagedActivation(model=self, stage_list=vehicle_steps,
                                         shuffle=False, shuffle_between_stages=False)
        # Variable to stop simulation if set to False.
        self.running = True
        # Duration for a simulation in hours.
        self.sim_time = sim_time
        # Time that passes for each step in minutes.
        self.resolution = time_resolution
        # List of timestamps for each simulation step.
        self.timestamps = pd.Series(pd.date_range('20230101 00:00:00',
                                                  periods=self.sim_time * (60 / self.resolution),
                                                  freq=f'{self.resolution}T'))  # .dt.time
        # The timestamp for the current step in a simulation.
        self.step_time = None

        # Agents--------------------------------------------------------------------------------------------

        vehicles = {'Group1': num_group1, 'Group2': num_group2, 'Group3': num_group3, 'Group4': num_group4}

        counter = 0
        for vehicle_type, vehicle_num in vehicles.items():
            for num in range(vehicle_num):
                obj = eval(vehicle_type)(unique_id=counter + num, station=self,
                                         params=self.vehicle_params[vehicle_type])
                self.schedule.add(obj)
            counter += vehicle_num

        for num in range(num_battery):
            obj = Battery(unique_id=counter + num, station=self, capacity=150, soc=100, limit=station_limit)
            self.schedule.add(obj)

        # List to contain all chargers at the station.
        self.charge_list = [Charger(power=350, num_sockets=4) for _ in range(num_charger)]

        # Data collector for model and agent variables.
        self.datacollector = DataCollector(
            model_reporters={'Power': self.get_station_power, 'Time': 'step_time'},
            agent_reporters={'Soc': 'soc', 'Arrival': 'arrival', 'Capacity': 'capacity', 'MaxCharge': 'max_charge'}
        )

    def get_station_power(self):
        """
        Finds the power used for all chargers to return the total power used at the station.

        Returns
        -------

        """
        power_sum = [charger.max_power - charger.accessible_power for charger in self.charge_list]
        return sum(power_sum)

    def step(self):
        """
        Actions to execute for each iteration of a simulation.
        """
        # Find correct timestamp of the current step.
        self.step_time = self.timestamps[self.schedule.steps]
        # Collect data from the current step.
        self.datacollector.collect(self)
        # Iterate through all agents (vehicles, batteries) in the model.
        self.schedule.step()
        # Reset variable for the next step. Checks if the power of each charger is updated.
        # self.power_updated = False


if __name__ == '__main__':
    pass
