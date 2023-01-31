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
        self.num = 0
        self.power = 350

    def new_request(self):
        """
        Add a new vehicle to the charger and update the maximum power delivered to each power outlet in use.

        Returns
        -------
        maximum power for each power outlet.
        """
        self.num += 1
        if self.num == 4:
            self.available = False
        self.power = 350 / self.num
        return self.power

    def remove_vehicle(self):
        """
        Remove a vehicle from the charger.
        """
        self.num -= 1
        self.available = True

