# -*- encoding: utf-8 -*-
"""
This file contains the simulation of charging station.
"""

__author__ = 'Lina Grünbeck / lina.grunbeck@gmail.com'

from chargingStationSim.station import Station
from chargingStationSim.visualization import station_plot
from chargingStationSim.visualization import vehicle_plot
from mesa.batchrunner import batch_run
from mesa.batchrunner import BatchRunner

# Duration of simulation in hours.
sim_time = 24
# Time resolution of each step in the simulation in minutes.
time_resolution = 10
# Number of steps the simulation requires.
num_steps = int((sim_time / time_resolution) * 60) - 1

# Set number of vehicles for each vehicle type.
# vehicles = (('Group_1', 5), ('Group_2', 20), ('Group_3', 15), ('Group_4', 10))

# Set model parameters for a simulation.
model_params = {'num_group1': 5, 'num_group2': 20, 'num_group3': 15, 'num_group4': 10,
                'num_battery': 0, 'num_charger': 6,
                'time_resolution': time_resolution, 'sim_time': sim_time}

# Start a simulation.
results = batch_run(
    model_cls=Station,
    parameters=model_params,
    iterations=10,
    max_steps=num_steps,
    number_processes=1,
    data_collection_period=1,
    display_progress=True,
)

save_path = 'C:/Users/linag/OneDrive - Norwegian University of Life Sciences/Master/Plot'

# Run functions for visualization of the simulation results.
station_data = station_plot(results, multirun=True, iterations=10, time_step=time_resolution / 60,
                            sim_duration=sim_time, path=save_path)
# vehicle_data = vehicle_plot(results)
