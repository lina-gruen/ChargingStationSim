# -*- encoding: utf-8 -*-
"""
This file contains the Battery class
"""

__author__ = 'Lina Grünbeck / lina.grunbeck@gmail.com'


class Battery:
    """
    Class for a local battery pack.
    """

    def __init__(self, capacity, soc):
        """
        Parameters
        ----------
        capacity: int
            Max kWh rating of the battery.
        soc: int
            State of Charge of the battery.
        """
        self.capacity = capacity
        self.soc = soc
        # self.max_pow = max_pow

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
        new_soc = self.soc + (available / self.capacity)
        if new_soc > 100:
            self.soc = 100
        else:
            self.soc = new_soc

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
        new_soc = self.soc - (demand / self.capacity)
        if new_soc < 0:
            self.soc = 0
        else:
            self.soc = new_soc
