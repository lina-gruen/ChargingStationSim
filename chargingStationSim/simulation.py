# -*- encoding: utf-8 -*-
"""
This file contains the simulation of charging station.
"""

__author__ = 'Lina Grünbeck / lina.grunbeck@gmail.com'


from chargingStationSim.station import Station

# Start a simulation.
model = Station(num_vehicle=6, num_battery=1, num_charger=2, time_step=15)
model.step()
