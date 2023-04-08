# -*- encoding: utf-8 -*-
"""
This file contains the simulation of charging station.
"""

__author__ = 'Lina Grünbeck / lina.grunbeck@gmail.com'

from chargingStationSim.station import Station
from chargingStationSim.visualization import station_plot
from chargingStationSim.visualization import vehicle_plot
from chargingStationSim.visualization import set_plotstyle
from chargingStationSim.mesa_mod.batchrunner import batch_run
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
# model_params = {'num_external': 32, 'num_internal': 67, 'num_charger': 5,
#                 'battery': True, 'station_limit': 2000, 'time_resolution': time_resolution, 'sim_time': sim_time}
model_params = [{'num_external': 32, 'num_internal': 67, 'num_charger': 5,
                 'battery': False, 'station_limit': 2000, 'time_resolution': time_resolution, 'sim_time': sim_time},
                 {'num_external': 32, 'num_internal': 45, 'num_charger': 6,
                 'battery': False, 'station_limit': 2000, 'time_resolution': time_resolution, 'sim_time': sim_time}
                 ]

Station.set_arrival_dist(resolution=time_resolution)
Station.set_break_dist()

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

# Run functions for visualization of the simulation results.
station_data = station_plot(results, multirun=True, flexibility=model_params[0]['battery'], iterations=num_runs,
                            path=save_path, runs=len(model_params))
vehicle_data = vehicle_plot(results, steps=num_steps, path=save_path, runs=len(model_params))

# record end time
end = time.time()

print("The time of execution of above program is :",
      (end-start), "s")
