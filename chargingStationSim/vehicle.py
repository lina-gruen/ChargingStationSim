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

    def __init__(self, unique_id, station, random, arrival, params):
        """
        Parameters
        ----------
        unique_id: int
            Id for the vehicle.
        station: mesa.model
            Instance of the station that contains the vehicle.
        arrival: pandas timestamp
            The arrival time of the vehicle at the station.
        params: dict
            Parameters for the vehicle.
                capacity: int
                    Max kWh rating of the vehicle battery.
                max_charge: int
                    Maximum power at which the vehicle can charge in kW.
        """
        super().__init__(unique_id, station)

        self.rand_generator = random
        self.station = station
        # Time per iteration step in minutes.
        self.resolution = station.resolution
        # Set the battery capacity and maximum charging power for the vehicle.
        self.capacity, self.max_charge = self.set_params(params)
        # State of Charge of the vehicle battery in percentage.
        self.soc = self.get_start_soc()
        # Arrival time at charging station.
        self.arrival = arrival
        # Maximum steps that the vehicle charges.
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
        self.state = {'charging': False, 'arrived': False, 'waiting': False}

    def get_start_soc(self):
        """
        Finds a soc for the vehicle from a probability distribution.

        Returns
        -------
        New soc for the vehicle.
        """
        # Gamma distribution with chosen parameter.
        return self.rand_generator.gamma(shape=3, scale=6)

    def set_params(self, params):
        """
        Finds a battery capacity and maximum charging power for the vehicle from a probability distribution.

        Parameters
        ----------
        params: dict
            Contains mean values for capacity and max_charge.

        Returns
        -------
        Chosen battery capacity and maximum charging power
        """
        # Normal distribution with chosen mean and standard deviation.
        capacity = self.rand_generator.choice(params['capacity'])
        max_charge = self.rand_generator.choice(params['max_charge'])
        return capacity, max_charge

    def get_arrival(self):
        """
        Finds iteration at which the vehicle first arrives at a charging station from a probability distribution.

        Returns
        -------
        New arrival time for the vehicle.
        """
        # Random choice from list with probability weights in p.
        arrival_step = self.rand_generator.choice(self.station.timestamps, p=self.arrival_dist)
        return arrival_step

    def get_rest_type(self):
        hour = pd.Timestamp(self.arrival).hour
        return self.rand_generator.choice(['kort', 'lang'], p=self.rest_dist[hour])

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
            self.state['arrived'] = True
        elif self.charge_steps == 0:
            self.state['arrived'] = True
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
            if not self.state['waiting']:
                self.state['waiting'] = True
                self.wait_time += self.resolution
                return
            else:
                self.wait_time += self.resolution
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
        if self.state['arrived']:
            pass
        elif self.state['charging']:
            pass
        elif self.state['waiting']:
            self.find_charger()
            # elif self.arrival == self.station.step_time.time():
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
            self.power = 0

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

    def __init__(self, unique_id, station, random, arrival, params, break_type):
        super().__init__(unique_id, station, random, arrival, params)

        self.type = 'External'
        self.break_type = break_type

        if self.break_type == 'ShortBreak':
            self.target_soc = 80
            self.charge_steps = self.get_charge_steps(mean=30, std=2)
        else:
            self.target_soc = 100
            self.charge_steps = self.get_charge_steps(mean=600, std=2)

        target_power = (self.target_soc * (self.capacity / 100) - self.soc) / (self.resolution / 60)
        if target_power >= self.max_charge:
            self.target_power = self.max_charge
        else:
            self.target_power = target_power

# ----------------------------------------------------------------------------------------------------------------------


class Internal(Vehicle):
    """
    Subclass for all internal vehicles.
    """

    def __init__(self, unique_id, station, random, arrival, params, break_type):
        super().__init__(unique_id, station, random, arrival, params)

        self.type = 'Internal'
        self.break_type = break_type
        if self.break_type == 'Internal':
            self.target_power = 50
            self.target_soc = 100
            self.charge_steps = self.get_charge_steps(mean=350, std=2)
        else:
            self.target_power = 50
            self.target_soc = 100
            self.charge_steps = self.get_charge_steps(mean=350, std=2)


