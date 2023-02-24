# -*- encoding: utf-8 -*-
"""
This file contains the Charger class
"""

__author__ = 'Lina Grünbeck / lina.grunbeck@gmail.com'


class Charger:
    """
    Class for a charger.
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
        self.socket_power = self.max_power
        self.used_power = 0

    def update_power(self):
        """
        Update the power delivered to each charging socket in use and the total power delivered by the whole charger.
        """
        if self.num_users != 0:
            self.socket_power = self.max_power / self.num_users
        else:
            self.socket_power = self.max_power

        # used_power == max_power when power is distributed equally between sockets in use.
        self.used_power = self.socket_power * self.num_users
        """
        Prøv å få til individuell effekt på hvert uttak dersom ulike effekter er ønskelig. Liste for socket_power?
        """

    def check_new_power(self):
        """
        Checks what the socket power would be if the charger got an additional user.

        Returns
        -------
        Socket power in kW.
        """
        return self.max_power / (self.num_users + 1)

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
