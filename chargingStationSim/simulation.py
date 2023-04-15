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
import pandas as pd
import time

# record start time
start = time.time()

# Location to save the results from the simulation.
save_path = 'C:/Users/linag/OneDrive - Norwegian University of Life Sciences/Master/Plot'
# Time resolution for each time step in the simulation in minutes.
time_resolution = 5
# For how many iterations the simulation should be repeated.
num_iter = 100
# If there should be a stationary battery at the station.
flexibility = False
# ID number of the run with the specific parameter combination. Should start at 0.
run_id = 5

# Set model parameters for a simulation.
model_params = {'num_external': 32, 'num_internal': 67, 'chargers': {350: 12, 500: 3},
                'battery': flexibility, 'station_limit': 2000, 'time_resolution': time_resolution}

# Parameters for each vehicle group containing arrays to randomly select params from.
vehicle_params = {'External': {'capacity': (500, 600, 700, 800, 900), 'max_charge': (350, 450, 500)},
                  'Internal': {'capacity': (500, 600, 700, 800, 900), 'max_charge': (350, 450, 500)}}

# Parameters for a stationary battery for flexibility.
battery_params = {'capacity': 1000, 'max_charge': 1000, 'soc': 90}

# Probability distribution for the arrival of vehicles at the station for a given hour in the day.
arrival_dist = {'Internal': [0.0000, 0.2500, 0.0000, 0.0000, 0.0000, 0.0000, 0.0952, 0.0000, 0.0000, 0.0476, 0.0000,
                             0.0000, 0.0000, 0.0000, 0.3214, 0.0595, 0.0595, 0.0000, 0.0238, 0.0357, 0.0714, 0.0357,
                             0.0000, 0.0000],
                'External': [0.0150, 0.0145, 0.0150, 0.0154, 0.0173, 0.0281, 0.0445, 0.0529, 0.0660, 0.0725, 0.0725,
                             0.0721, 0.0707, 0.0702, 0.0664, 0.0580, 0.0487, 0.0440, 0.0374, 0.0314, 0.0276, 0.0243,
                             0.0192, 0.0164]}

# Probability distribution for a vehicles to have a short break at the station for a given hour in the day.
short_break = {'Internal': [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 1.00, 0.00, 0.00, 0.00, 0.00, 0.52,
                            0.00, 0.00, 0.00, 1.00, 0.00, 0.00, 0.00, 0.00, 0.00],
               'External': [0.50, 0.25, 0.25, 0.67, 0.95, 0.89, 0.88, 0.70, 0.83, 0.90, 0.84, 0.79, 0.70, 0.60, 0.55,
                            0.31, 0.21, 0.23, 0.27, 0.24, 0.27, 0.27, 0.18, 0.28]}

# alternative internal: [0.13, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.58, 0.70, 0.00, 0.00, 0.00, 0.52,
#  0.44, 0.17, 0.17, 0.24, 0.32, 0.04, 0.13, 0.13, 0.13]

# Probability distribution for a vehicles to have a medium long break at the station for a given hour in the day.
medium_break = {'Internal': [0.00, 1.00, 0.00, 0.00, 0.00, 0.00, 1.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.15,
                             1.00, 0.80, 0.00, 0.00, 1.00, 1.00, 1.00, 0.00, 0.00],
                'External': [0, 0, 0, 0, 0, 0, 0, 0 , 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}

# Probability distribution for a vehicles to have a long break at the station for a given hour in the day.
long_break = {'Internal': [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.33,
                           0.00, 0.20, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
              'External': [0.50, 0.75, 0.75, 0.33, 0.05, 0.11, 0.12, 0.30, 0.17, 0.10, 0.16, 0.21, 0.30, 0.40, 0.45,
                           0.69, 0.79, 0.77, 0.73, 0.76, 0.73, 0.73, 0.82, 0.72]}

# alternative internal: [0.87, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 0.42, 0.30, 0.00, 0.00, 0.00, 0.48,
#  0.56, 0.83, 0.83, 0.76, 0.68, 0.96, 0.87, 0.87, 0.87]

# Set the parameters for the simulation globally for the Station class.
Station.set_params(vehicle=vehicle_params, battery=battery_params, flexibility=flexibility)
Station.set_arrival_dist(arrival=arrival_dist, resolution=time_resolution)
Station.set_break_dist(short_break=short_break, medium_break=medium_break, long_break=long_break)

# Number of steps the simulation requires in one iteration.
num_steps = int((24 / time_resolution) * 60) - 1

# Start a simulation.
results = batch_run(
    model_cls=Station,
    parameters=model_params,
    run_id=run_id,
    iterations=num_iter,
    max_steps=num_steps,
    number_processes=1,
    data_collection_period=1,
    display_progress=True,
)

data = pd.DataFrame(results)

if flexibility:
    data.to_csv(save_path + f'/simulation_{run_id}_flex.csv', index=False)
else:
    data.to_csv(save_path + f'/simulation_{run_id}.csv', index=False)

# Set custom matplotlib style.
# set_plotstyle()

# Run functions for visualization of the simulation results.
# station_data = station_plot(results, multirun=True, flexibility=flexibility, iterations=num_runs,
#                            path=save_path)
# vehicle_data = vehicle_plot(results, steps=num_steps, path=save_path)

# record end time
end = time.time()

print("The time of execution of above program is :",
      (end - start), "s")
