# -*- encoding: utf-8 -*-
"""
The file contains the Vehicle class.
"""

__author__ = 'Lina Grünbeck / lina.grunbeck@gmail.com'

from chargingStationSim.mesa_mod import Agent
import pandas as pd


# Seed for randomization.
# rand_generator = default_rng(seed=1257)


class Vehicle(Agent):
    """
    Base class for all vehicles in a vehicle fleet.
    """

    def __init__(self, unique_id, station, random, arrival, capacity, max_charge, soc):
        """
        Parameters
        ----------
        unique_id: int
            Id for the vehicle.
        station: mesa.model
            Instance of the station that contains the vehicle.
        random: numpy random generator instance

        arrival: pandas timestamp
            The arrival time of the vehicle at the station.
        capacity: int
            Max kWh rating of the vehicle battery.
        max_charge: int
            Maximum power at which the vehicle can charge in kW.
        soc: float
            State of Charge of the battery at initialization.
        """
        super().__init__(unique_id, station)

        self.rand_generator = random
        self.station = station
        # Time per iteration step in minutes.
        self.resolution = station.resolution
        # Set the battery capacity and maximum charging power for the vehicle.
        self.capacity = capacity
        self.max_charge = max_charge
        # State of Charge of the vehicle battery in percentage.
        self.soc = soc
        # Arrival time at charging station.
        self.arrival = arrival
        # Default maximum steps that the vehicle charges.
        self.charge_steps = self.get_charge_steps(mean=45, std=2)
        # Counter for the amount of minutes the vehicle has to stand in line at the station.
        self.wait_time = 0
        # Wished charging power when searching for a charger.
        self.target_power = None
        # Wished end soc when charging.
        self.target_soc = None
        # The power the vehicle is currently charging with.
        self.power = 0
        # The charger the vehicle is using. None if not charging.
        self.charger = None
        # Current state of the vehicle.
        self.state = dict(charging=False, waiting=False, done=False, left=False)
        # If the vehicle ever got to charge in the simulation.
        self.no_charge = False

    def get_charge_steps(self, mean, std):
        """
        Finds the maximum amount of steps the vehicle wants to charge from a probability distribution.

        Returns
        -------
        Max steps available for charging.
        """
        time = self.rand_generator.normal(loc=mean, scale=std)
        steps = int(time / self.resolution)
        return steps

    def update_charge_power(self):
        """
        Updates the current charging power if charger has more available power since last step in
        case another vehicle disconnected.
        """
        if self.power < self.charger.accessible_power < self.target_power:
            new_power = self.charger.accessible_power
            self.charger.accessible_power -= (new_power - self.power)
            self.power = new_power
        elif self.charger.accessible_power >= self.target_power:
            new_power = self.target_power
            self.charger.accessible_power -= (new_power - self.power)
            self.power = new_power

    def update_soc(self):
        """
        Updates the soc of the vehicle when charging.
        """
        # Update charging power if charger has more available power since last step.
        if self.power != self.target_power:
            self.update_charge_power()
        # How many kWh can be charged in the current step with the chosen power.
        step_capacity = self.power * (self.resolution / 60)  # min/60=h
        # Find new soc.
        new_soc = self.soc + (step_capacity / self.capacity) * 100
        self.charge_steps -= 1
        if new_soc >= self.target_soc:
            self.soc = self.target_soc
            self.state['done'] = True
        elif self.charge_steps == 0:
            self.state['done'] = True
            self.soc = round(new_soc, 2)
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

    def find_charger(self):
        """
        Finds charger that can deliver the requested power. If nothing is available the vehicle waits until next step.
        """
        # All charger that are available and the power they can deliver.
        available = [(charger, charger.accessible_power) for charger in self.station.charge_list if charger.available]
        if not available:
            self.check_waiting()
            return
        # Find the charger for which the accessible power is closest to the target power of the vehicle.
        charger = available[min(range(len(available)), key=lambda num: abs(available[num][1] - self.target_power))]
        # If what's available is less or equal to the requested power we take all the available power:
        if charger[1] <= self.target_power:
            self.connect_charger(charger[0], charger[1])
        # If the requested power is less than what's available we only take what was requested:
        else:
            self.connect_charger(charger[0], self.target_power)

    def check_vehicle(self):
        """
        Checks which action to take for a vehicle.
        """
        if self.state['left']:
            pass
        elif self.state['charging']:
            pass
        elif self.state['waiting'] or self.arrival == self.station.step_time:
            self.find_charger()
            # elif self.arrival == self.station.step_time.time():
        else:
            pass

    def step_1(self):
        """
        Removes the vehicle from its charger if it finished charging in the previous step.
        """
        if self.state['done']:
            self.state['charging'] = False
            self.charger.remove_vehicle(self.power)
            self.charger = None
            self.power = 0
            self.state['done'] = False
            self.state['left'] = True

    def step_2(self):
        """
        Finds out what action to take for the vehicle and charges if the vehicle is connected to a charger.
        """
        self.check_vehicle()
        if self.state['charging']:
            self.update_soc()

# ----------------------------------------------------------------------------------------------------------------------


class External(Vehicle):
    """
    Subclass for all external vehicles.
    """

    def __init__(self, unique_id, station, random, arrival, capacity, max_charge, soc, break_type):
        super().__init__(unique_id, station, random, arrival, capacity, max_charge, soc)

        self.type = 'External'
        self.break_type = break_type

        if self.break_type == 'ShortBreak':
            self.target_soc = 80
            # maximum steps that the vehicle has time to charge.
            self.charge_steps = self.get_charge_steps(mean=35, std=1)
        else:
            self.target_soc = 100
            self.charge_steps = self.get_charge_steps(mean=660, std=6)

        # target_power = (self.target_soc * (self.capacity / 100) - self.soc) / (self.resolution / 60)
        target_power = ((0.6 * self.capacity) / (self.resolution * self.charge_steps)) * \
                       (self.target_soc - self.soc)

        if target_power >= self.max_charge:
            self.target_power = self.max_charge
        else:
            self.target_power = target_power

    def check_waiting(self):
        if not self.state['waiting']:
            self.state['waiting'] = True
        self.charge_steps -= 1
        self.wait_time += self.resolution
        if self.break_type == 'ShortBreak' and self.wait_time == 20 or \
           self.break_type == 'LongBreak' and self.wait_time == 180:
            self.state['waiting'] = False
            self.state['left'] = True
            self.no_charge = True

# ----------------------------------------------------------------------------------------------------------------------


class Internal(Vehicle):
    """
    Subclass for all internal vehicles.
    """

    def __init__(self, unique_id, station, random, arrival, capacity, max_charge, soc, break_type):
        super().__init__(unique_id, station, random, arrival, capacity, max_charge, soc)

        self.type = 'Internal'
        self.break_type = break_type

        if self.break_type == 'ShortBreak':
            self.target_soc = 80
            # maximum steps that the vehicle has time to charge.
            self.charge_steps = self.get_charge_steps(mean=120, std=3)
        elif self.break_type == 'MediumBreak':
            self.target_soc = 100
            self.charge_steps = self.get_charge_steps(mean=270, std=3)
        else:
            self.target_soc = 100
            self.charge_steps = self.get_charge_steps(mean=630, std=3)

        # target_power = ((self.target_soc * (self.capacity / 100)) - self.soc) / (self.resolution / 60)
        target_power = ((0.6 * self.capacity) / (self.resolution * self.charge_steps)) * \
                       (self.target_soc - self.soc)

        if target_power >= self.max_charge:
            self.target_power = self.max_charge
        else:
            self.target_power = target_power

    def check_waiting(self):
        if not self.state['waiting']:
            self.state['waiting'] = True
        self.charge_steps -= 1
        self.wait_time += self.resolution
        if self.charge_steps == 0:
            self.state['waiting'] = False
            self.state['left'] = True
            self.no_charge = True