# -*- encoding: utf-8 -*-
"""
The file contains the Vehicle class
"""

__author__ = 'Lina Grünbeck / lina.grunbeck@gmail.com'

from mesa import Agent
import pandas as pd
from numpy.random import default_rng
import random

random.seed(1256)
rand_generator = default_rng(seed=1256)


class Vehicle(Agent):
    """
    Base class for all vehicles in a vehicle fleet.
    """

    default_params = {'weight': None, 'dist_type': None, 'capacity': None, 'efficiency': None, 'max_charge': None}

    def __init__(self, unique_id, station, params):
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
        """
        self.station = station
        # Time per iteration step in minutes.
        self.resolution = station.resolution
        self.weight = params['weight']
        self.dist_type = params['dist_type']
        self.capacity = params['capacity']
        self.efficiency = params['efficiency']
        self.max_charge = params['max_charge']
        # Arrival time at charging station.
        self.arrival = self.get_arrival()
        # State of Charge of the vehicle battery.
        self.soc = self.get_soc()
        # kWh needed for the vehicle.
        # self.demand = 0
        self.target_power = self.max_charge
        # The power the vehicle is currently charging with.
        self.power = 0
        # The charger the vehicle is using. None if not charging.
        self.charger = None
        # Current state of the vehicle.
        self.state = {'charging': False, 'arrived': False, 'waiting': False}

    @staticmethod
    def get_soc():
        """
        Finds a soc for the vehicle from a probability distribution.

        Returns
        -------
        New soc for the vehicle.
        """
        # random.randint(0, 90)
        return rand_generator.gamma(shape=3, scale=6)

    def get_arrival(self):
        """
        Finds iteration at which the vehicle first arrives at a charging station from a probability distribution.

        Returns
        -------
        New arrival time for the vehicle.
        """
        # arrival_hour = random.randint(0, 23)
        # arrival_step = random.randint((arrival_hour * (60 / self.resolution)) + 1,
        #                              (arrival_hour + 1) * (60 / self.resolution))
        arrival_step = rand_generator.choice(self.station.timestamps, p=None)
        return arrival_step

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
        # Update charging power if charger has more available power since last step (another vehicle disconnected).
        if self.power < self.charger.accessible_power < self.target_power:
            self.power = self.charger.accessible_power
        elif self.charger.accessible_power >= self.target_power:
            self.power = self.target_power
        # how many kWh can be charged in the current step with the chosen power.
        step_capacity = self.power * (self.resolution / 60)  # min/60=h

        new_soc = self.soc + (step_capacity / self.capacity) * 100
        if new_soc >= 100:
            self.soc = 100
            self.state['arrived'] = True
        else:
            self.soc = round(new_soc, 2)

    def connect_charger(self, char_choice, pow_choice):
        """
        Connect the vehicle to the chosen charger and sets the charging power to the chosen level.

        Parameters
        ----------
        char_choice: Instance of the Charger class
            The chosen charger.
        pow_choice: int
            The chosen power.
        """
        if self.state['waiting']:
            self.state['waiting'] = False
        self.state['charging'] = True
        self.charger = char_choice
        self.power = pow_choice
        self.charger.add_vehicle(self.power)
        # self.charger.update_power()

    def find_charger(self):
        """
        Finds charger that can deliver the requested power. If nothing is available the vehicle waits until next step.
        """
        # All charger that are available and the power they can deliver.
        available = [(charger, charger.accessible_power) for charger in self.station.charge_list if charger.available]
        if not available:
            self.state['waiting'] = True
            return
        # Find the charger for which the accessible power is closest to the target power of the vehicle.
        charger = available[min(range(len(available)), key=lambda num: abs(available[num][1] - self.target_power))]
        # If what's available is less or equal to the requested power we take all the available power:
        if charger[1] <= self.target_power:
            self.connect_charger(charger[0], charger[1])
        # If the requested power is less than what's available we only take what was requested:
        else:
            self.connect_charger(charger[0], self.target_power)

    # def find_charger(self):
    #     """
    #     Uses charger if one is free, else waits until next simulation step to check again.
    #     """

    #     def charger_found(choice):
    #         if self.state['waiting']:
    #             self.state['waiting'] = False
    #         self.state['charging'] = True
    #         self.charger = choice
    #         self.charger.add_vehicle()
    #         self.charger.update_power()

    #     best_choice = (None, 0)
    #     for charger in self.station.charge_list:
    #         if charger.available:
    #             power = charger.check_new_power()
    #             if power == charger.max_power:
    #                 charger_found(charger)
    #                 break
    #             elif power > best_choice[1]:
    #                 best_choice = (charger, power)

    #     if not self.state['charging'] and best_choice[0] is not None:
    #         charger_found(best_choice[0])
    #     elif not self.state['charging'] and not self.state['waiting']:
    #         self.state['waiting'] = True

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
        elif self.arrival == self.station.step_time:
            self.find_charger()
        else:
            pass

    def step_1(self):
        """
        Removes the vehicle from its charger if it finished charging in the previous step.
        """
        if self.state['charging'] and self.state['arrived']:
            self.state['charging'] = False
            self.charger.remove_vehicle(self.power)
            self.charger = None

    def step_2(self):
        """
        Finds out what action to take for the vehicle and charges if the vehicle is connected to a charger.
        """
        # Update the power of all chargers once before charging all vehicles.
        # if not self.station.power_updated:
        #     for charger in self.station.charge_list:
        #         charger.update_power()
        #     self.station.power_updated = True

        self.check_vehicle()
        if self.state['charging']:
            self.update_soc()


class Group1(Vehicle):
    """
    Subclass for all group1 vehicles.
    """

    def __init__(self, vehicle_id, station, params, arrival):
        super().__init__(vehicle_id, station, params, arrival)

    def get_arrival(self):
        """
        Finds iteration at which the vehicle first arrives at a charging station from a probability distribution.

        Returns
        -------
        New arrival time for the vehicle.
        """
        arrival_step = rand_generator.choice(self.station.timestamps, p=None)
        return arrival_step


class Group2(Vehicle):
    """
    Subclass for all group2 vehicles.
    """

    def __init__(self, vehicle_id, station, params, arrival):
        super().__init__(vehicle_id, station, params, arrival)

    def get_arrival(self):
        """
        Finds iteration at which the vehicle first arrives at a charging station from a probability distribution.

        Returns
        -------
        New arrival time for the vehicle.
        """
        arrival_step = rand_generator.choice(self.station.timestamps, p=None)
        return arrival_step
        return arrival_step


class Group3(Vehicle):
    """
    Subclass for all group3 vehicles.
    """

    def __init__(self, vehicle_id, station, params, arrival):
        super().__init__(vehicle_id, station, params, arrival)

    def get_arrival(self):
        """
        Finds iteration at which the vehicle first arrives at a charging station from a probability distribution.

        Returns
        -------
        New arrival time for the vehicle.
        """
        arrival_step = rand_generator.choice(self.station.timestamps, p=None)
        return arrival_step
        return arrival_step


class Group4(Vehicle):
    """
    Subclass for all group4 vehicles.
    """

    def __init__(self, vehicle_id, station, params, arrival):
        super().__init__(vehicle_id, station, params, arrival)

    def get_arrival(self):
        """
        Finds iteration at which the vehicle first arrives at a charging station from a probability distribution.

        Returns
        -------
        New arrival time for the vehicle.
        """
        arrival_step = rand_generator.choice(self.station.timestamps, p=None)
        return arrival_step
        return arrival_step
