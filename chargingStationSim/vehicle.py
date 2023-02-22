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

    default_params = {'weight_class': None, 'dist_type': None, 'capacity': None, 'efficiency': None}

    def __init__(self, vehicle_id, station, params, soc, arrival):
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
                    Efficiency of the battery measured in kWh/km.
        soc: int
            State of Charge of the vehicle battery.
        """
        self.id = vehicle_id
        self.station = station
        self.time = station.time_step  # time per iteration step in hours (decimal if resolution is less than 1 hour).
        self.weight_class = params['weight_class']
        self.dist_type = params['dist_type']
        self.capacity = params['capacity']
        if params['efficiency'] is None:
            self.efficiency = 5
        else:
            self.efficiency = params['efficiency']
        # Start soc.
        self.soc = soc
        # Iteration at which the vehicle first arrives at a charging station.
        self.arrival = arrival
        # kWh needed for the vehicle.
        # self.demand = 0
        '''
        # The power the vehicle is currently charging with.
        self.power = 0
        '''
        # Current state of the vehicle.
        self.state = {'charging': False, 'driving': False, 'waiting': False}
        # The charger the vehicle is using. None if not charging.
        self.charger = None
        # self.max_pow = params['max_pow']

    def arrival_soc(self):
        """
        Finds the soc at the vehicle's arrival from a probability distribution.

        Returns
        -------

        """
        pass

    def drive(self):
        """
        Updates the soc of the vehicle when driving.
        """
        speed = 60  # km/h
        driving_demand = (self.efficiency * speed * self.time) / 60
        new_soc = self.soc - (driving_demand / self.capacity) * 100
        if new_soc <= 0:
            self.soc = 0
            self.state['driving'] = False
            self.state['waiting'] = True
        else:
            self.soc = round(new_soc, 2)

    def update_soc(self):
        """
        Updates the soc of the vehicle when charging.
        """
        '''
        target soc for charging the total kWh demand (enten 100 eller utifra demand, utifra
        om det er lokal eller langdistanse.)
        # target_soc = self.soc + (self.demand / self.capacity) * 100
        '''
        # how many kWh can be charged per iteration step with current power.
        step_demand = self.charger.socket_power * (self.time / 60)  # min/60=h
        '''
        Sjå om ein faktisk trenge å oppdatere iter_demand hver runde. if self.power == self.charger.socket_power: pass
        '''
        new_soc = self.soc + (step_demand / self.capacity) * 100
        if new_soc >= 100:
            self.soc = 100
            self.state['charging'] = False
            self.charger.remove_vehicle()
            self.charger = None
            self.state['driving'] = True
        else:
            self.soc = round(new_soc, 2)

    def find_charger(self):
        """
        Uses charger if one is free, else waits until next iteration to check again.
        """
        for charger in self.station.charge_list:
            if charger.available:
                self.state['waiting'] = False
                self.state['charging'] = True
                self.charger = charger
                self.charger.add_vehicle()
                break
            else:
                pass

    def check_vehicle(self):
        """
        Checks which action to take for a vehicle.
        """
        if self.state['charging']:
            pass
        elif self.state['driving']:
            self.drive()
        elif self.state['waiting']:
            self.find_charger()
        elif self.arrival == self.station.schedule.steps:
            self.find_charger()

    def step_1(self):
        """
        Vehicle actions to execute for the first stage of each iteration of a simulation.
        """
        self.check_vehicle()

    def step_2(self):
        """
        Vehicle actions to execute for the second stage of each iteration of a simulation.
        """
        for charger in self.station.charge_list:
            charger.update_power()
        if self.state['charging']:
            self.update_soc()
