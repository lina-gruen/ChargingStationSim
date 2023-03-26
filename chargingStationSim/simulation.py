# -*- encoding: utf-8 -*-
"""
This file contains the simulation of charging station.
"""

__author__ = 'Lina Grünbeck / lina.grunbeck@gmail.com'

from chargingStationSim.station import Station
from chargingStationSim.visualization import station_plot
from chargingStationSim.visualization import vehicle_plot
from chargingStationSim.visualization import set_plotstyle
from mesa.batchrunner import batch_run
import time

# record start time
start = time.time()

# Duration of simulation in hours.
sim_time = 24
# Time resolution of each step in the simulation in minutes.
time_resolution = 10
# Number of steps the simulation requires.
num_steps = int((sim_time / time_resolution) * 60) - 1
# How many times the simulation should be repeated.
num_runs = 10

# Set model parameters for a simulation.
model_params = {'num_fastcharge': 15, 'num_break': 25, 'num_night': 25, 'num_internal': 67, 'num_charger': 20,
                'battery': True, 'station_limit': 2000, 'time_resolution': time_resolution, 'sim_time': sim_time}

# Start a simulation.
results = batch_run(
    model_cls=Station,
    parameters=model_params,
    iterations=num_runs,
    max_steps=num_steps,
    number_processes=1,
    data_collection_period=1,
    display_progress=True,
)

save_path = 'C:/Users/linag/OneDrive - Norwegian University of Life Sciences/Master/Plot'

# Set custom matplotlib style.
set_plotstyle()

if model_params['battery']:
    # Run functions for visualization of the simulation results.
    station_data = station_plot(results, multirun=True, flexibility=True, iterations=num_runs,
                                path=save_path, run_nr=1)
else:
    station_data = station_plot(results, multirun=True, flexibility=False, iterations=num_runs,
                                path=save_path, run_nr=1)

# vehicle_data = vehicle_plot(results)

# record end time
end = time.time()

print("The time of execution of above program is :",
      (end-start), "s")
