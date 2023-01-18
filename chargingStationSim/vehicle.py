# -*- encoding: utf-8 -*-
"""
The file contains the Vehicle class
"""

__author__ = 'Lina Grünbeck / lina.grunbeck@gmail.com'


class Vehicle:
    """
    Base class for all vehicles in a vehicle fleet.
    """

    default_params = {'weight_class': None, 'dist_type': None, 'capacity': None, 'efficiency': None,
                      'drive_dist': None, 'soc': None}

    def __init__(self, params):
        """
        Parameters
        ----------
        params: dict
            New parameters for a battery.
            Including:
                weight_class: string
                    If vehicle is medium-heavy or heavy
                dist_type: string
                    If the vehicle is for short-distance (local) or
                    long-distance travel.
                capacity: int
                    Max kWh rating of the vehicle battery.
                efficiency: int
                    Efficiency of the battery measured in km/kWh.
                drive_dist: int
                    Length of the next trip planned in km.
                soc: int
                    State of Charge of the vehicle battery.
        """
        self.weight_class = params['weight_class']
        self.dist_type = params['dist_type']
        self.capacity = params['capacity']
        self.efficiency = params['efficiency']
        self.drive_dist = params['drive_dist']
        self.soc = params['soc']
        self.demand = None
        self.wait_time = None
        # self.max_pow = params['max_pow']

    def get_soc(self):
        """"
        Returns the current SOC of the vehicle.
        """
        return self.soc

    def new_demand(self, new_dist, rest):
        """
        Calculate the new demand of kWh the vehicle has for its next trip.
        """
        if rest:
            self.wait_time = 90
        else:
            self.demand = self.default_eff / new_dist

    def charge_vehicle(self, power):
        """
        Charge the vehicle by a certain amount.
        """
        pass
