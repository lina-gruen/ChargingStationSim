# -*- encoding: utf-8 -*-
"""
This file contains the simulation of charging station.
"""

__author__ = 'Lina Grünbeck / lina.grunbeck@gmail.com'

from chargingStationSim.station import Station
from chargingStationSim.visualization import station_plot
from chargingStationSim.visualization import vehicle_plot
from mesa.batchrunner import batch_run


# Duration of simulation in hours.
sim_time = 24
# Time resolution of each step in the simulation in minutes.
time_step = 10
# Number of steps the simulation requires.
num_steps = int((sim_time/time_step)*60)

# Set model parameters for a simulation.
model_params = {'num_vehicle': 20, 'num_battery': 0, 'num_charger': 2, 'time_step': 60/time_step}

# Start a simulation.
results = batch_run(
    model_cls=Station,
    parameters=model_params,
    iterations=1,
    max_steps=num_steps,
    number_processes=1,
    data_collection_period=1,
    display_progress=True,
)

# Run functions for visualization of the simulation results.
station_plot(results)
vehicle_plot(results)
