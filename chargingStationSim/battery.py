# -*- encoding: utf-8 -*-
"""
This file contains the Battery class
"""

__author__ = 'Lina Grünbeck / lina.grunbeck@gmail.com'

from mesa import Agent


class Battery(Agent):
    """
    Class for a local battery pack.
    """

    def __init__(self, unique_id, station, capacity, soc, station_limit):
        super().__init__(unique_id, station)
        """
        Parameters
        ----------
        unique_id: int
            Id for the battery.
        station: mesa.model
            Instance of the station that contains the battery.
        capacity: int
            Max kWh rating of the battery.
        soc: int
            Initial state of Charge of the battery.
        """
        self.station = station
        self.capacity = capacity
        self.soc = soc
        # The power limit of the station the battery is connected to.
        self.limit = station_limit
        # How much power the battery is currently using. Positive if discharging and negative if recharging.
        self.power = 0

    def recharge(self, available):
        """
        Recharge the battery a certain amount.

        Parameters
        ----------
        available: int
            Amount of kWh given to the battery.
        """
        if available < 0:
            raise ValueError('Battery was given negative amount of kWh.')
        new_soc = self.soc + (available / self.capacity)*100
        if new_soc > 100:
            self.soc = 100
        else:
            self.soc = round(new_soc, 2)

    def discharge(self, demand):
        """
        Discharge the battery a certain amount.

        Parameters
        ----------
        demand: int
            Amount of kWh needed from the battery.
        """
        if demand < 0:
            raise ValueError('Demanded negative amount of kWh from battery.')
        new_soc = self.soc - (demand / self.capacity)*100
        if new_soc < 0:
            self.soc = 0
        else:
            self.soc = round(new_soc, 2)

    def step_1(self):
        """
        Battery actions to execute for the first stage of each iteration of a simulation.
        """
        pass

    def step_2(self):
        """
        Battery actions to execute for the second stage of each iteration of a simulation.
        """
        # if
        # self.station.batt_power = self.station.get_station_power() - self.station.power_limit
        pass



