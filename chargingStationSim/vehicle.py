# -*- encoding: utf-8 -*-
"""
The file contains the Vehicle class
"""

__author__ = 'Lina Grünbeck / lina.grunbeck@gmail.com'

from mesa import Agent


class Vehicle(Agent):
    """
    Base class for all vehicles in a vehicle fleet.
    """

    default_params = {'weight_class': None, 'dist_type': None, 'capacity': None, 'efficiency': None,
                      'drive_dist': None}
    # resolution = 600  # 10min

    def __init__(self, vehicle_id, station, params, soc):
        super().__init__(vehicle_id, station)
        """
        Parameters
        ----------
        vehicle_id: int
            Unique id for the battery.
        station: mesa.model
            Instance of the station that contains the vehicle.
        params: dict
            New parameters for the vehicle.
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
        self.id = vehicle_id
        self.station = station
        self.weight_class = params['weight_class']
        self.dist_type = params['dist_type']
        self.capacity = params['capacity']
        self.drive_dist = params['drive_dist']
        self.soc = soc
        if params['efficiency'] is None:
            self.efficiency = 5
        else:
            self.efficiency = params['efficiency']
        self.demand = 0
        self.driving = 0
        self.charge = False
        # self.wait_time = None
        # self.max_pow = params['max_pow']

    def get_soc(self):
        """
        Return the current SOC of the vehicle.
        """
        return self.soc

    @staticmethod
    def new_route_len():
        """
        Find the new driving distance for the vehicles next trip after charging.

        Returns
        -------
        route_len: int
            new driving distance.
        """
        route_len = 75
        return route_len

    def new_demand(self, route_len):
        """
        Calculate the new demand of kWh the vehicle needs for its next trip.
        """
        self.demand = route_len / self.efficiency
        # target_soc enten 100 eller utifra demand, utifra om det er lokal eller langdistanse.

    def update_soc(self):
        """
        Update the soc of the vehicle when charging.
        """
        if self.demand < 0:
            raise ValueError('Vehicle was given negative amount of kWh.')
        new_soc = self.soc + (self.demand / self.capacity) * 100
        if new_soc > 100:
            self.soc = 100
        else:
            self.soc = round(new_soc, 2)
            self.charge = False

    def find_charger(self):
        """
        Uses charger if one is free, else waits until one becomes free.
        """
        for charger in self.station.charge_list:
            if charger.available:
                self.charge = True
                charger.available = False
                self.new_demand(self.new_route_len())
                self.update_soc()
                break

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

    def charge_vehicle(self, power):
        """
        Charge the vehicle by a certain amount.
        """
        pass

    def step(self):
        """
        Vehicle actions to execute for each iteration of a simulation.
        """
        print(f'Vehicle id: {self.id}, soc: {self.soc}')
        self.check_vehicle()
        print(f'Vehicle id: {self.id}, soc: {self.soc}')
