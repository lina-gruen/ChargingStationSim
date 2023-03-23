# -*- encoding: utf-8 -*-
"""
This file contains the Station class.
"""

__author__ = 'Lina Grünbeck / lina.grunbeck@gmail.com'

from chargingStationSim.battery import Battery
from chargingStationSim.charger import Charger
from chargingStationSim.vehicle import ExternalFastCharge, ExternalBreak, ExternalNight, Internal
from mesa import Model
# from mesa.time import BaseScheduler
from mesa.time import StagedActivation
from mesa.datacollection import DataCollector
import pandas as pd


class Station(Model):
    """
    Class for a charging station.
    """

    # Parameters for each vehicle group containing mean values to use in a probability distribution.
    vehicle_params = {ExternalFastCharge: {'capacity': (100, 150, 200), 'max_charge': (150, 200, 250),
                                           'arrival_dist': [1, 1, 1, 1, 1, 1, 1, 1,
                                                            1, 2, 2, 4, 7, 7, 4, 2,
                                                            2, 1, 1, 1, 1, 1, 1, 1]},
                      ExternalBreak: {'capacity': (250, 300, 350), 'max_charge': (200, 250, 350),
                                      'arrival_dist': [1, 1, 1, 1, 1, 1, 1, 1,
                                                       1, 2, 2, 4, 7, 7, 4, 2,
                                                       2, 1, 1, 1, 1, 1, 1, 1]},
                      ExternalNight: {'capacity': (250, 300, 350), 'max_charge': (350, 400, 450),
                                      'arrival_dist': [1, 1, 1, 1, 1, 1, 1, 1,
                                                       1, 1, 1, 4, 7, 7, 2, 4,
                                                       7, 7, 2, 2, 1, 1, 1, 1]},
                      Internal: {'capacity': (200, 250, 300), 'max_charge': (200, 250, 350),
                                 'arrival_dist': [1, 1, 1, 1, 1, 1, 1, 1,
                                                  1, 1, 1, 1, 1, 1, 1, 1,
                                                  2, 4, 7, 7, 4, 2, 1, 1]}}

    battery_params = {'capacity': 1000, 'max_charge': 1000, 'soc': 100}

    def __init__(self, num_fastcharge, num_break, num_night, num_internal, num_charger,
                 battery, station_limit, time_resolution, sim_time):
        """
        Parameters
        ----------
        num_fastcharge : int
        num_break : int
        num_night : int
        num_internal : int
        num_charger: int
        battery: bool
        station_limit: int
        time_resolution: int
        sim_time: int
        """
        super().__init__()

        # Station-------------------------------------------------------------------------------------------------------

        num_vehicles = {ExternalFastCharge: num_fastcharge, ExternalBreak: num_break, ExternalNight: num_night,
                        Internal: num_internal}

        # Simulation----------------------------------------------------------------------------------------------------

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
        # The timestamp for the current step in a simulation.
        self.step_time = None
        # List of timestamps for each simulation step.
        self.timestamps = pd.Series(pd.date_range('20230101 00:00:00',
                                                  periods=self.sim_time * (60 / self.resolution),
                                                  freq=f'{self.resolution}T'))

        # Agents--------------------------------------------------------------------------------------------------------

        counter = 0
        for vehicle_type, vehicle_num in num_vehicles.items():
            # Set the probability distribution for arrival times for the current vehicle type.
            vehicle_type.set_arrival_dist(self.vehicle_params[vehicle_type]['arrival_dist'], self.resolution)
            for num in range(vehicle_num):
                obj = vehicle_type(unique_id=counter + num,
                                   station=self,
                                   params=self.vehicle_params[vehicle_type])
                self.schedule.add(obj)
            counter += vehicle_num

        if battery:
            #
            self.batt_power = 0
            obj = Battery(unique_id=counter + 1,
                          station=self,
                          capacity=self.battery_params['capacity'],
                          max_charge=self.battery_params['max_charge'],
                          soc=self.battery_params['soc'],
                          station_limit=station_limit)
            self.schedule.add(obj)

        # List to contain all chargers at the station.
        self.charge_list = [Charger(power=350, num_sockets=4) for _ in range(num_charger)]

        # Data collector for model and agent variables.
        self.datacollector = DataCollector(
            model_reporters={'Power': [self.get_station_power, [battery]], 'Time': 'step_time',
                             'Batt_power': 'batt_power'},
            agent_reporters={'Soc': 'soc', 'Arrival': 'arrival', 'Capacity': 'capacity', 'Type': 'type',
                             'power': 'power'}
        )

    def get_station_power(self, battery):
        """
        Finds the power used for all chargers to return the total power used at the station.

        Returns
        -------

        """
        power_sum = [charger.max_power - charger.accessible_power for charger in self.charge_list]
        if battery:
            return sum(power_sum) - self.batt_power
        else:
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


if __name__ == '__main__':
    pass
