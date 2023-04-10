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

# Duration of simulation in hours.
sim_time = 24
# Time resolution of each step in the simulation in minutes.
time_resolution = 10
# Number of steps the simulation requires in one iteration.
num_steps = int((sim_time / time_resolution) * 60) - 1
# For how many iterations the simulation should be repeated.
num_iter = 10
# If there should be a stationary battery at the station.
flexibility = False
# ID number of the run with the specific parameter combination. Should start on 0.
run_id = 0

# Set model parameters for a simulation.
model_params = {'num_external': 32, 'num_internal': 67, 'num_charger': 5,
                'battery': flexibility, 'station_limit': 2000, 'time_resolution': time_resolution,
                'sim_time': sim_time}

Station.set_arrival_dist(resolution=time_resolution)
Station.set_break_dist()

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

save_path = 'C:/Users/linag/OneDrive - Norwegian University of Life Sciences/Master/Plot'

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
