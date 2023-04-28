# -*- encoding: utf-8 -*-
"""
This file contains the Battery class
"""

__author__ = 'Lina Grünbeck / lina.grunbeck@gmail.com'

from chargingStationSim.mesa_mod import Agent


class Battery(Agent):
    """
    Class for a local battery pack.
    """

    def __init__(self, unique_id, station, capacity, max_charge, soc, station_limit):
        super().__init__(unique_id, station)
        """
        Parameters
        ----------
        unique_id: int
            Id for the battery.
        station: mesa_mod.model
            Instance of the station that contains the battery.
        capacity: int
            Max kWh rating of the battery.
        soc: int
            Initial state of Charge of the battery.
        """
        self.station = station
        # Time per iteration step in minutes.
        self.resolution = station.resolution
        # Label to sort agents by under visualization.
        self.type = 'Battery'
        # Capacity of the battery in kWh.
        self.capacity = capacity
        # The maximum charging power of the battery.
        self.max_charge = max_charge
        # State of Charge of the vehicle battery in percentage.
        self.soc = soc
        #
        self.wait_time = 0
        # Upper limit for the soc of the battery.
        self.upper_soc_limit = 100
        # Lower limit for the soc of the battery.
        self.lower_soc_limit = 0
        # How much power the battery is currently using to recharge/discharge.
        self.power = 0
        # Check if the battery is drained or fully charged at initialization.
        if self.soc <= self.lower_soc_limit:
            self.empty = True
        else:
            self.empty = False
        if self.soc >= self.upper_soc_limit:
            self.full = True
        else:
            self.full = False
        # The upper power limit at the station for when the battery starts discharging.
        self.limit = station_limit

        self.arrival = None
        self.break_type = None
        self.no_charge = False

    def recharge(self):
        """
        Recharge the battery a certain amount to consume local power.
        """
        # How many kWh can be charged in the current step with the chosen power.
        step_capacity = self.power * (self.resolution / 60)  # min/60=h
        new_soc = self.soc + (step_capacity / self.capacity)*100
        if new_soc > self.upper_soc_limit:
            # Adjust the power to the amount we need to get exactly to the upper soc limit.
            self.power = (self.upper_soc_limit - self.soc) * 0.6 * (self.capacity / self.resolution)
            self.soc = self.upper_soc_limit
            self.full = True
        elif new_soc == self.upper_soc_limit:
            self.soc = self.upper_soc_limit
            self.full = True
        else:
            self.soc = round(new_soc, 2)
        if self.empty:
            self.empty = False

    def discharge(self):
        """
        Discharge the battery a certain amount to give the station local power.
        """
        # How many kWh can the battery give in the current step with the chosen power.
        step_capacity = self.power * (self.resolution / 60)  # min/60=h
        new_soc = self.soc - (step_capacity / self.capacity)*100
        if new_soc < self.lower_soc_limit:
            # Adjust the power to the amount we need to get exactly to the lower soc limit.
            self.power = (self.soc - self.lower_soc_limit) * 0.6 * (self.capacity / self.resolution)
            self.soc = self.lower_soc_limit
            self.empty = True
        elif new_soc == self.lower_soc_limit:
            self.soc = self.lower_soc_limit
            self.empty = True
        else:
            self.soc = round(new_soc, 2)
        self.power = -self.power
        if self.full:
            self.full = False

    def step_1(self):
        """
        Battery actions to execute for the first stage of each iteration of a simulation.
        """
        pass

    def step_2(self):
        """
        Battery actions to execute for the second stage of each iteration of a simulation.
        """
        station_power = self.station.get_station_power(battery=False)
        if station_power > self.limit and not self.empty:
            if (station_power - self.limit) >= self.max_charge:
                self.power = self.max_charge
            else:
                self.power = station_power - self.limit
            self.discharge()
            self.station.batt_power = self.power
        # elif station_power < self.charge_limit and not self.full:
        #     if (self.charge_limit - station_power) >= self.max_charge:
        #         self.power = self.max_charge
        #     else:
        #         self.power = self.charge_limit - station_power
        #     self.recharge()
        #     self.station.batt_power = self.power
        # else:
        #     self.power = 0
        #     self.station.batt_power = self.power
        elif station_power < self.limit and not self.full:
            if self.limit / 2 < station_power:
                if (self.limit - station_power) >= self.max_charge:
                    self.power = self.max_charge
                else:
                    self.power = self.limit - station_power
            else:
                if (self.limit / 2 - station_power) >= self.max_charge:
                    self.power = self.max_charge
                else:
                    self.power = self.limit / 2 - station_power
            self.recharge()
            self.station.batt_power = self.power
        else:
            self.power = 0
            self.station.batt_power = self.power
