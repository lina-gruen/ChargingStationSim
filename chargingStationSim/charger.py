# -*- encoding: utf-8 -*-
"""
This file contains the Charger class
"""

__author__ = 'Lina Grünbeck / lina.grunbeck@gmail.com'


class Charger:
    """
    Class for a charger connected to a charging station.
    """

    def __init__(self, power, num_sockets):
        """
        Parameters
        ----------
        power: int
            Total power that the charger can deliver.
        num_sockets: int
            Number of charging sockets on the charger.
        """
        self.available = True
        self.num_users = 0
        self.num_sockets = num_sockets
        self.max_power = power
        self.accessible_power = self.max_power

    def add_vehicle(self, used_power):
        """
        Add a new vehicle to the charger.
        """
        self.num_users += 1
        self.accessible_power -= used_power
        if self.accessible_power == 0 or self.num_users == self.num_sockets:
            self.available = False

    def remove_vehicle(self, freed_power):
        """
        Remove a vehicle from the charger.
        """
        self.num_users -= 1
        self.accessible_power += freed_power
        self.available = True
