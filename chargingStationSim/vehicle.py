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
            Unique id for the vehicle.
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
        self.time = station.time_step  # time per iteration step in minutes
        self.weight_class = params['weight_class']
        self.dist_type = params['dist_type']
        self.capacity = params['capacity']
        self.drive_dist = params['drive_dist']
        if params['efficiency'] is None:
            self.efficiency = 5
        else:
            self.efficiency = params['efficiency']
        self.soc = soc
        # kWh needed for the vehicle.
        self.demand = 0
        # number of iterations the vehicle will be driving.
        self.driving = 0
        '''
        # The power the vehicle is currently charging with.
        self.power = 0
        '''
        # The charger the vehicle is using. None if not charging.
        self.charger = None
        # If the vehicle is charging or not.
        self.charging = False
        # self.wait_time = None
        # self.max_pow = params['max_pow']

    def get_soc(self):
        """
        Return the current SOC of the vehicle.
        """
        return self.soc

    def new_demand(self):
        """
        Calculate the new demand of kWh the vehicle needs for its next
        trip, depending on the length of the new route.
        """
        route_len = 75
        self.demand = route_len / self.efficiency
        # self.driving = ...
        '''
        Må finne ut hvor mye demand tilsvarer driving til neste kjøretur.
        '''

    def update_soc(self):
        """
        Update the soc of the vehicle when charging.
        """

        '''
        target soc for charging the total kWh demand (enten 100 eller utifra demand, utifra
        om det er lokal eller langdistanse.)
        # target_soc = self.soc + (self.demand / self.capacity) * 100
        '''

        # how many kWh can be charged per iteration step with current power.
        step_demand = self.charger.socket_power * (self.time / 60)
        '''
        Sjå om ein faktisk trenge å oppdatere iter_demand hver runde. if self.power == self.charger.socket_power: pass
        '''
        new_soc = self.soc + (step_demand / self.capacity) * 100
        if new_soc >= 100:
            self.soc = 100
            self.charging = False
            self.charger.remove_vehicle()
            self.charger = None
            # self.driving = ... ?
        else:
            self.soc = round(new_soc, 2)

    def find_charger(self):
        """
        Uses charger if one is free, else waits until next iteration to check again.
        """
        for charger in self.station.charge_list:
            if charger.available:
                self.charging = True
                self.charger = charger
                self.charger.add_vehicle()
                self.new_demand()
                break
            else:
                pass

    def check_vehicle(self):
        """
        Check which action to take for a vehicle.
        """
        if self.charging:
            pass
        elif self.driving == 0:
            self.find_charger()
        else:
            self.driving -= 1

    def step_1(self):
        """
        Vehicle actions to execute for the first stage of each iteration of a simulation.
        """
        self.check_vehicle()

    def step_2(self):
        """
        Vehicle actions to execute for the second stage of each iteration of a simulation.
        """
        print(f'Vehicle id: {self.id}, Charger id: {self.charger.id}, soc: {self.soc}')

        for charger in self.station.charge_list:
            if charger.num_users != 0:
                charger.update_power()
        if self.charging:
            self.update_soc()

        if self.charging:
            print(f'Vehicle id: {self.id}, Charger id: {self.charger.id}, soc: {self.soc} '
                  f'\n----------------------------------------')
        else:
            print(f'Vehicle id: {self.id}, Charger id: None, soc: {self.soc} '
                  f'\n----------------------------------------')
