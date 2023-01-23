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
        self.drive_dist = params['drive_dist']
        self.soc = params['soc']
        if params['efficiency'] is None:
            self.efficiency = 5
        else:
            self.efficiency = params['efficiency']
        self.demand = None
        self.charge = False
        # self.wait_time = None
        # self.max_pow = params['max_pow']

    def get_soc(self):
        """
        Return the current SOC of the vehicle.
        """
        return self.soc

    def update_soc(self):
        """

        """
        if ... < 0:
            raise ValueError('Vehicle was given negative amount of kWh.')
        new_soc = self.soc + (... / self.capacity) * 100
        if new_soc > 100:
            self.soc = 100
        else:
            self.soc = new_soc
            self.charge = False

    def find_charger(self, charge_list):
        """
        Uses charger if one is free, else waits until one becomes free.

        Parameters
        ----------
        charge_list: list
            list of bools telling which chargers are occupied.
        """
        if charge_list:
            self.charge = True
            self.new_demand()
            self.update_soc()
        else:
            pass

    def check_vehicle(self):
        """
        Check which action to take for a vehicle.
        """
        if self.charge:
            self.update_soc()
        elif self.driving == 0:
            self.find_charger()
        else:
            self.driving -= 1

    def new_demand(self, new_dist, rest):
        """
        Calculate the new demand of kWh the vehicle has for its next trip.
        """
        pass
        # self.demand = self.default_params['efficiency'] / new_dist

    def charge_vehicle(self, power):
        """
        Charge the vehicle by a certain amount.
        """
        pass
