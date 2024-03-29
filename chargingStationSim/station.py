# -*- encoding: utf-8 -*-
"""
This file contains the Station class.
"""

__author__ = 'Lina Grünbeck / lina.grunbeck@gmail.com'

from chargingStationSim.battery import Battery
from chargingStationSim.charger import Charger
from chargingStationSim.vehicle import External, Internal
from chargingStationSim.mesa_mod.model import Model
from chargingStationSim.mesa_mod.time import StagedActivation
from chargingStationSim.mesa_mod.datacollection import DataCollector
import pandas as pd
import numpy as np
from numpy.random import default_rng


class Station(Model):
    """
    Class for a charging station.
    """
    rand_generator = default_rng(seed=1256)

    # Parameters for each vehicle group containing arrays to randomly select params from.
    vehicle_params = None
    # Parameters for a stationary battery for flexibility.
    battery_params = None
    # Probability distribution for the arrival of vehicles at the station for a given hour in the day.
    arrival_dist = {'Internal': None,
                    'External': None}
    # Probability distribution for a vehicles to have a short break at the station for a given hour in the day.
    short_break = {'Internal': None,
                   'External': None}
    # Probability distribution for a vehicles to have a long break at the station for a given hour in the day.
    long_break = {'Internal': None,
                  'External': None}
    # Will contain the probability of a vehicle having either a short or a long breaks for a given hour in the day.
    break_dist = {'Internal': None,
                  'External': None}

    @classmethod
    def set_seed(cls, seed):
        """
        Sets seed for randomization.
        """
        cls.rand_generator = default_rng(seed=seed)

    @classmethod
    def set_params(cls, vehicle, battery, flexibility):
        """
        Sets new vehicle and battery parameters for the Station.
        """
        cls.vehicle_params = vehicle
        if flexibility:
            cls.battery_params = battery

    @classmethod
    def set_arrival_dist(cls, arrival, resolution):
        """
        Sets new probability distribution for the arrival of vehicles at the station.
        """
        for vehicle in ('Internal', 'External'):
            if not len(arrival[vehicle]) == 24:
                raise KeyError(f'Invalid length given for {vehicle} arrival distribution.')
            else:
                extended_dist = []
                for weight in arrival[vehicle]:
                    for _ in range(int(60 / resolution)):
                        extended_dist.append(weight)
                extended_dist = extended_dist / np.sum(extended_dist)
                cls.arrival_dist[vehicle] = extended_dist

    @classmethod
    def set_break_dist(cls, short_break, medium_break, long_break):
        """
        Sets new probability distribution for the type of mandatory rest periods vehicles have at the station.
        """
        for vehicle in ('Internal', 'External'):
            if not len(short_break[vehicle]) == 24 or not len(medium_break[vehicle]) == 24 \
                    or not len(long_break[vehicle]) == 24:
                raise KeyError(f'Invalid length given for one of the {vehicle} break distributions.')
            else:
                dist = []
                for short, medium, long in zip(short_break[vehicle], medium_break[vehicle], long_break[vehicle]):
                    dist.append((short, medium, long))
                cls.break_dist[vehicle] = dist

    def __init__(self, num_external, num_internal, chargers, battery, station_limit, time_resolution):
        """
        Parameters
        ----------
        num_external: int
        num_internal : int
        chargers: int
        battery: bool
        station_limit: int
        time_resolution: int
        """
        super().__init__()

        if self.arrival_dist is None:
            raise ValueError('No arrival distribution was given.')
        elif self.short_break is None:
            raise ValueError('No break distributions were given.')

        # Station-------------------------------------------------------------------------------------------------------

        num_vehicles = {'External': num_external, 'Internal': num_internal}

        # Simulation----------------------------------------------------------------------------------------------------

        # Make a scheduler that splits each iteration into two steps
        vehicle_steps = ['step_1', 'step_2']
        self.schedule = StagedActivation(model=self, stage_list=vehicle_steps,
                                         shuffle=False, shuffle_between_stages=False)
        # Variable to stop simulation if set to False.
        self.running = True
        # Duration for a simulation in hours.
        self.sim_time = 24
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
            for num in range(vehicle_num):
                arrival_time = self.rand_generator.choice(self.timestamps, p=self.arrival_dist[vehicle_type])
                hour = pd.Timestamp(arrival_time).hour
                break_type = self.rand_generator.choice(['ShortBreak', 'MediumBreak', 'LongBreak'],
                                                        p=self.break_dist[vehicle_type][hour])
                cap = self.rand_generator.choice(self.vehicle_params[vehicle_type]['capacity'],
                                                 p=[0.15, 0.22, 0.29, 0.22, 0.12])
                charge = self.rand_generator.choice(self.vehicle_params[vehicle_type]['max_charge'],
                                                    p=[0.14, 0.18, 0.21, 0.26, 0.21])
                soc = self.rand_generator.normal(loc=50, scale=6)
                obj = eval(vehicle_type)(unique_id=counter + num,
                                         station=self,
                                         random=self.rand_generator,
                                         capacity=cap,
                                         max_charge=charge,
                                         arrival=arrival_time,
                                         soc=soc,
                                         break_type=break_type)
                self.schedule.add(obj)
            counter += vehicle_num

        if battery:
            # Add a local battery pack to the agent schedule.
            self.batt_power = 0
            obj = Battery(unique_id=counter + 1,
                          station=self,
                          capacity=self.battery_params['capacity'],
                          max_charge=self.battery_params['max_charge'],
                          soc=self.battery_params['soc'],
                          station_limit=station_limit)
            self.schedule.add(obj)

        # List to contain all chargers at the station.
        self.charge_list = []
        for power, num in chargers.items():
            self.charge_list.extend([Charger(power=power, num_sockets=4) for _ in range(num)])

        # Data collector for model and agent variables.
        self.datacollector = DataCollector(
            model_reporters={'Power': [self.get_station_power, [battery]], 'Time': 'step_time',
                             'Batt_power': 'batt_power'},
            agent_reporters={'Soc': 'soc', 'Arrival': 'arrival', 'Capacity': 'capacity',
                             'Type': 'type', 'BreakType': 'break_type', 'power': 'power',
                             'Waiting': 'wait_time', 'Charged': 'no_charge'})

    def get_station_power(self, battery):
        """
        Finds the power used for all chargers to return the total power used at the station.

        Returns
        -------
        Total station power.
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
