# -*- encoding: utf-8 -*-
"""
This file contains the Station class.
"""

__author__ = 'Lina Grünbeck / lina.grunbeck@gmail.com'

from chargingStationSim.battery import Battery
from chargingStationSim.charger import Charger
from chargingStationSim.vehicle import External, Internal
from mesa import Model
# from mesa.time import BaseScheduler
from mesa.time import StagedActivation
from mesa.datacollection import DataCollector
import pandas as pd
import numpy as np
from numpy.random import default_rng

# Seed for randomization.
rand_generator = default_rng(seed=1256)


class Station(Model):
    """
    Class for a charging station.
    """

    # Parameters for each vehicle group containing arrays to randomly select params from.
    vehicle_params = {External: {'capacity': (500, 600, 700, 800, 900), 'max_charge': (350, 450, 500)},
                      Internal: {'capacity': (500, 600, 700, 800, 900), 'max_charge': (350, 450, 500)}}

    # Parameters for a stationary battery for flexibility.
    battery_params = {'capacity': 1000, 'max_charge': 1000, 'soc': 90}

    # Probability distribution for the arrival of vehicles at the station for a given hour in the day.
    arrival_dist = [1.0, 1.0, 1.0, 1.1, 1.2, 1.9, 3.1, 3.6, 4.5, 5.0, 5.0, 5.0,
                    4.9, 4.8, 4.6, 4.0, 3.4, 3.0, 2.6, 2.2, 1.9, 1.7, 1.3, 1.1]

    # Probability distribution for a vehicles to have a short break at the station for a given hour in the day.
    short_break = [0.50, 0.25, 0.25, 0.67, 0.95, 0.89, 0.88, 0.70, 0.83, 0.90, 0.84, 0.79, 0.70, 0.60, 0.55, 0.31, 0.21,
                   0.23, 0.27, 0.24, 0.27, 0.27, 0.18, 0.28]

    # Probability distribution for a vehicles to have a long break at the station for a given hour in the day.
    long_break = [0.50, 0.75, 0.75, 0.33, 0.05, 0.11, 0.12, 0.30, 0.17, 0.10, 0.16, 0.21, 0.30, 0.40, 0.45, 0.69, 0.79,
                  0.77, 0.73, 0.76, 0.73, 0.73, 0.82, 0.72]

    # Will contain the probability of a vehicle having either a short or a long breaks for a given hour in the day.
    break_dist = None

    @classmethod
    def set_arrival_dist(cls, resolution):
        """
        Sets new probability distribution for the arrival of vehicles at the station.
        """
        if not len(cls.arrival_dist) == 24:
            raise KeyError('Invalid length given for arrival distribution.')
        else:
            extended_dist = []
            for weight in cls.arrival_dist:
                for _ in range(int(60 / resolution)):
                    extended_dist.append(weight)
            extended_dist = extended_dist / np.sum(extended_dist)
            cls.arrival_dist = extended_dist

    @classmethod
    def set_break_dist(cls):
        """
        Sets new probability distribution for the type of mandatory rest periods vehicles have at the station.
        """
        if not len(cls.short_break) == 24 or not len(cls.short_break) == 24:
            raise KeyError('Invalid length given for one of the break distributions.')
        else:
            dist = []
            for short, long in zip(cls.short_break, cls.long_break):
                dist.append((short, long))
            cls.break_dist = dist

    def __init__(self, num_external, num_internal, num_charger, battery, station_limit, time_resolution, sim_time):
        """
        Parameters
        ----------
        num_external: int
        num_internal : int
        num_charger: int
        battery: bool
        station_limit: int
        time_resolution: int
        sim_time: int
        """
        super().__init__()

        # Station-------------------------------------------------------------------------------------------------------

        num_vehicles = {External: num_external, Internal: num_internal}

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
        # self.day = pd.Series(pd.date_range('20230101 00:00:00',
        #                                    periods=24 * (60 / self.resolution),
        #                                    freq=f'{self.resolution}T')).dt.time

        # Agents--------------------------------------------------------------------------------------------------------

        counter = 0
        for vehicle_type, vehicle_num in num_vehicles.items():
            # Set the probability distribution for arrival times for the current vehicle type.
            # Vehicle.set_arrival_dist(self.arrival_dist, self.resolution)
            # Vehicle.set_rest_dist(self.short_break, self.long_break)
            if vehicle_type == Internal:
                for num in range(vehicle_num):
                    arrival_time = rand_generator.choice(self.timestamps, p=self.arrival_dist)
                    obj = vehicle_type(unique_id=counter + num,
                                       station=self,
                                       random=rand_generator,
                                       params=self.vehicle_params[vehicle_type],
                                       arrival=arrival_time,
                                       break_type='Internal')
                    self.schedule.add(obj)
                counter += vehicle_num
            else:
                for num in range(vehicle_num):
                    arrival_time = rand_generator.choice(self.timestamps, p=self.arrival_dist)
                    hour = pd.Timestamp(arrival_time).hour
                    break_type = rand_generator.choice(['ShortBreak', 'LongBreak'], p=self.break_dist[hour])
                    obj = vehicle_type(unique_id=counter + num,
                                       station=self,
                                       random=rand_generator,
                                       params=self.vehicle_params[vehicle_type],
                                       arrival=arrival_time,
                                       break_type=break_type)
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
                             'power': 'power',  'Waiting': 'wait_time', 'BreakType': 'break_type'}
        )

    def get_station_power(self, battery):
        """
        Finds the power used for all chargers to return the total power used at the station.

        Returns
        -------

        """
        power_sum = [charger.max_power - charger.accessible_power for charger in self.charge_list]
        if battery:
            return sum(power_sum) + self.batt_power
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
