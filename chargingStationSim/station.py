# -*- encoding: utf-8 -*-
"""
This file contains the Station class.
"""

__author__ = 'Lina Grünbeck / lina.grunbeck@gmail.com'

from chargingStationSim.battery import Battery
from chargingStationSim.charger import Charger
from chargingStationSim.vehicle import Vehicle, ExternalFastCharge, ExternalBreak, ExternalNight, Internal
from mesa import Model
# from mesa.time import BaseScheduler
from mesa.time import StagedActivation
from mesa.datacollection import DataCollector
import pandas as pd


class Station(Model):
    """
    Class for a charging station.
    """

    # Parameters for each vehicle group containing arrays to randomly select params from.
    vehicle_params = {ExternalFastCharge: {'capacity': (500, 600, 700, 800, 900), 'max_charge': (350, 450, 500)},
                      ExternalBreak: {'capacity': (500, 600, 700, 800, 900), 'max_charge': (350, 450, 500)},
                      ExternalNight: {'capacity': (500, 600, 700, 800, 900), 'max_charge': (350, 450, 500)},
                      Internal: {'capacity': (500, 600, 700, 800, 900), 'max_charge': (350, 450, 500)}}

    arrival_dist = [1.0, 1.0, 1.0, 1.1, 1.2, 1.9, 3.1, 3.6, 4.5, 5.0, 5.0, 5.0,
                    4.9, 4.8, 4.6, 4.0, 3.4, 3.0, 2.6, 2.2, 1.9, 1.7, 1.3, 1.1]

    short_rest_dist = [3, 1, 1, 4, 35, 49, 36, 26, 30, 54, 46, 37, 33, 27, 24, 18, 16, 14, 13, 9, 7, 4, 2, 5]

    long_rest_dist = [3, 3, 3, 2, 2, 6, 5, 11, 6, 6, 9, 10, 14, 18, 20, 41, 59, 47, 36, 29, 19, 11, 9, 13]

    battery_params = {'capacity': 1000, 'max_charge': 1000, 'soc': 90}

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
        # self.day = pd.Series(pd.date_range('20230101 00:00:00',
        #                                    periods=24 * (60 / self.resolution),
        #                                    freq=f'{self.resolution}T')).dt.time

        # Agents--------------------------------------------------------------------------------------------------------

        counter = 0
        for vehicle_type, vehicle_num in num_vehicles.items():
            # Set the probability distribution for arrival times for the current vehicle type.
            Vehicle.set_arrival_dist(self.arrival_dist, self.resolution)
            Vehicle.set_rest_dist(self.short_rest_dist, self.long_rest_dist)
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
                             'power': 'power',  'Waiting': 'wait_time'}
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
