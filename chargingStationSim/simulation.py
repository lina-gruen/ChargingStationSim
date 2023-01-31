# -*- encoding: utf-8 -*-
"""
This file contains the simulation of charging station.
"""

__author__ = 'Lina Grünbeck / lina.grunbeck@gmail.com'


from chargingStationSim.station import Station

# Start a simulation.
model = Station(6, 1, 1, 15)
model.step()
