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

# Set model parameters for a simulation.
model_params = {'num_fastcharge': 15, 'num_break': 25, 'num_night': 25, 'num_internal': 67,
                'num_battery': 0, 'num_charger': 20,
                'station_limit': 2000, 'time_resolution': time_resolution, 'sim_time': sim_time}

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

# Set custom matplotlib style.
set_plotstyle()
# Run functions for visualization of the simulation results.
station_data = station_plot(results, multirun=True, iterations=10, time_step=time_resolution / 60,
                            sim_duration=sim_time, path=save_path)
# vehicle_data = vehicle_plot(results)

# for power in station_data['Power']:
#     if power < 0:
#         print(True)
#     else:
#         print(False)

# record end time
end = time.time()

print("The time of execution of above program is :",
      (end-start), "s")
