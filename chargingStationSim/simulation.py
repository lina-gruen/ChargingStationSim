# -*- encoding: utf-8 -*-
"""
This file contains the simulation of charging station.
"""

__author__ = 'Lina Grünbeck / lina.grunbeck@gmail.com'

from chargingStationSim.station import Station
from mesa.batchrunner import batch_run
import pandas as pd
import matplotlib.pyplot as plt

# Duration of simulation in hours.
sim_time = 24
# Time resolution of each step in the simulation in minutes.
time_step = 10
# Number of steps the simulation requires.
num_steps = int((sim_time/time_step)*60)

# Set model parameters for a simulation.
model_params = {'num_vehicle': 6, 'num_battery': 0, 'num_charger': 2, 'time_step': 60/time_step}

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

# Print results from the simulation as a dataframe.
vehicle_df = pd.DataFrame(results)
vehicle_df.set_index(['Step', 'AgentID'], inplace=True)
station_df = pd.DataFrame(results)
station_df.set_index(['Step'], inplace=True)

# Find final soc of all vehicles.
end_soc = vehicle_df.xs(num_steps, level='Step')['Soc']
plt.figure()
end_soc.hist(bins=range(int(vehicle_df.Soc.max()) + 1))
# plt.show()

# Chosen arrival times for each vehicle.
start_arrival = vehicle_df.xs(0, level='Step')['Arrival']
arrival = vehicle_df.xs(1, level='AgentID')['Arrival']

# Plot development of the soc for all vehicles.
plt.figure()
for vehicle in range(model_params['num_vehicle']):
    plt.plot(vehicle_df.xs(vehicle, level='AgentID')['Soc'], marker='o', label=f'#{vehicle} soc')
    plt.legend()
    plt.show()
