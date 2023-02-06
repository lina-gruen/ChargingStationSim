# -*- encoding: utf-8 -*-
"""
This file contains the Charger class
"""

__author__ = 'Lina Grünbeck / lina.grunbeck@gmail.com'


class Charger:
    """
    Class for a charger.
    """

    def __init__(self, charger_id):
        """
        Parameters
        ----------
        charger_id: int
            Unique id for the charger.
        """
        self.id = charger_id
        self.available = True
        self.num_users = 0
        self.num_sockets = 4
        self.power = 350
        self.socket_power = 0

    def update_power(self):
        """
        Update and return the maximum power delivered to each charging socket in use.
        """
        self.socket_power = self.power / self.num_users

    def add_vehicle(self):
        """
        Add a new vehicle to the charger.

        Returns
        -------
        maximum power for each power outlet.
        """
        self.num_users += 1
        if self.num_users == self.num_sockets:
            self.available = False

    def remove_vehicle(self):
        """
        Remove a vehicle from the charger.
        """
        self.num_users -= 1
        self.available = True

