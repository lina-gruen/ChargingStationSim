# -*- encoding: utf-8 -*-
"""
The file contains the Vehicle class
"""

__author__ = 'Lina Grünbeck / lina.grunbeck@gmail.com'

from mesa import Agent
import random
random.seed(1256)


class Vehicle(Agent):
    """
    Base class for all vehicles in a vehicle fleet.
    """

    default_params = {'weight': None, 'dist_type': None, 'capacity': None, 'efficiency': None, 'max_charge': None}

    def __init__(self, unique_id, station, params, arrival):
        super().__init__(unique_id, station)
        """
        Parameters
        ----------
        unique_id: int
            Id for the vehicle.
        station: mesa.model
            Instance of the station that contains the vehicle.
        params: dict
            Parameters for the vehicle.
                weight: string
                    Weight class category og the vehicle.
                dist_type: string
                    If the vehicle is for short-distance (local) or
                    long-distance travel.
                capacity: int
                    Max kWh rating of the vehicle battery.
                efficiency: int
                    Efficiency of the battery measured in kWh/km.
                max_charge: int
                    Maximum power at which the vehicle can charge in kW.
        arrival: int
            Iteration at which the vehicle first arrives at a charging station.
        """
        self.station = station
        self.time = station.time_step  # time per iteration step in hours (decimal if resolution is less than 1 hour).
        self.weight = params['weight']
        self.dist_type = params['dist_type']
        self.capacity = params['capacity']
        self.efficiency = params['efficiency']
        self.max_charge = params['max_charge']
        self.arrival = arrival
        # State of Charge of the vehicle battery.
        self.soc = self.get_soc()
        # kWh needed for the vehicle.
        # self.demand = 0
        '''
        # The power the vehicle is currently charging with.
        self.power = 0
        '''
        # Current state of the vehicle.
        self.state = {'charging': False, 'arrived': False, 'waiting': False}
        # The charger the vehicle is using. None if not charging.
        self.charger = None

    @staticmethod
    def get_soc():
        """
        Finds a soc for the vehicle from a probability distribution.

        Returns
        -------
        New soc for the vehicle.
        """
        return random.randint(0, 90)

    # def drive(self):
    #     """
    #     Updates the soc of the vehicle when driving.
    #     """
    #     speed = 60  # km/h
    #     driving_demand = (self.efficiency * speed * self.time) / 60
    #     new_soc = self.soc - (driving_demand / self.capacity) * 100
    #     if new_soc <= 0:
    #         self.soc = 0
    #         self.state['driving'] = False
    #         self.state['waiting'] = True
    #     else:
    #         self.soc = round(new_soc, 2)

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
            self.state['arrived'] = True
        else:
            self.soc = round(new_soc, 2)

    def find_charger(self):
        """
        Uses charger if one is free, else waits until next simulation step to check again.
        """
        def charger_found(choice):
            if self.state['waiting']:
                self.state['waiting'] = False
            self.state['charging'] = True
            self.charger = choice
            self.charger.add_vehicle()
            self.charger.update_power()

        best_choice = (None, 0)
        for charger in self.station.charge_list:
            if charger.available:
                power = charger.check_new_power()
                if power == charger.max_power:
                    charger_found(charger)
                    break
                elif power > best_choice[1]:
                    best_choice = (charger, power)

        if not self.state['charging'] and best_choice[0] is not None:
            charger_found(best_choice[0])
        elif not self.state['charging'] and not self.state['waiting']:
            self.state['waiting'] = True

        # def closest_value(power_list, target):
        #     """
        #     Finds the available power output closest to the target power.
        #
        #     Parameters
        #     ----------
        #     power_list
        #     target
        #
        #     Returns
        #     -------
        #     Position
        #     """
        #     return power_list[min(range(len(power_list)), key=lambda num: abs(power_list[num] - target))]

    def check_vehicle(self):
        """
        Checks which action to take for a vehicle.
        """
        if self.state['arrived']:
            pass
        elif self.state['charging']:
            pass
        # elif self.state['driving']:
        #     self.drive()
        elif self.state['waiting']:
            self.find_charger()
        elif self.arrival == self.station.schedule.steps:
            self.find_charger()
        else:
            pass

    def step_1(self):
        """
        Vehicle actions to execute for the first stage of each iteration of a simulation.
        """
        self.check_vehicle()

    def step_2(self):
        """
        Vehicle actions to execute for the second stage of each iteration of a simulation.
        """
        # Update the power of all chargers once before charging all vehicles.
        if not self.station.power_updated:
            for charger in self.station.charge_list:
                charger.update_power()
            self.station.power_updated = True

        if self.state['charging']:
            self.update_soc()


class Group1(Vehicle):
    """
    Subclass for all group1 vehicles.
    """

    def __init__(self, vehicle_id, station, params, arrival):
        super().__init__(vehicle_id, station, params, arrival)
