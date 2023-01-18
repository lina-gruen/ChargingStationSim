# -*- encoding: utf-8 -*-
"""
The file contains the Vehicle class
"""

__author__ = 'Lina Grünbeck / lina.grunbeck@gmail.com'


class Vehicle:
    """
    Base class for the all vehicles in a vehicle fleet.
    """
    #Default efficiency measured in km/kWh.
    default_eff = 5

    def __init__(self, weight_class, dist_type, capacity, adapter, max_pow, drive_dist, soc):
        """

        """
        self.weight_class = weight_class
        self.dist_type = dist_type
        self.capacity = capacity
        self.adapter = adapter
        self.max_pow = max_pow
        self.drive_dist = drive_dist
        self.soc = soc
        self.demand = None
        self.wait_time = None

    def new_demand(self, new_dist, rest):
        """

        :return:
        """
        if rest:
            self.wait_time = 90
        else:
            self.demand = self.default_eff/new_dist

    def charge_vehicle(self, power):
        """

        :return:
        """
