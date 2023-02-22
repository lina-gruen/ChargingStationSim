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


# Station data -------------------------------------------------------------

station_df = pd.DataFrame(results)
# Convert 10 min resolution to single minutes.
station_df['Step'] *= 10
station_df.set_index(['Step'], inplace=True)

# Development of the station power.
plt.figure()
plt.plot(station_df.xs('Power', axis=1))
plt.xlabel('Time [min]')
plt.ylabel('Power [kW]')
plt.show()


# Vehicle data -------------------------------------------------------------

vehicle_df = pd.DataFrame(results)
vehicle_df['Step'] *= 10
vehicle_df.set_index(['Step', 'AgentID'], inplace=True)

# Final soc of all vehicles.
"""
end_soc = vehicle_df.xs(num_steps, level='Step')['Soc']
plt.figure()
end_soc.hist(bins=range(int(vehicle_df.Soc.max()) + 1))
plt.show()
"""

# Chosen arrival times for each vehicle.
# xs() returns a specific section of the dataframe based on index level and row values.
start_arrival = vehicle_df.xs(0, level='Step')['Arrival']
plt.figure()
start_arrival.hist(bins=range(int(vehicle_df.Arrival.max()) + 1))
plt.xlabel('Time [min/10]')
plt.ylabel('Number of vehicles')
plt.show()

# Development of the soc for all vehicles.
"""
plt.figure()
for vehicle in range(model_params['num_vehicle']):
    plt.plot(vehicle_df.xs(vehicle, level='AgentID')['Soc'], marker='o', label=f'#{vehicle} soc')
    plt.legend()
    plt.show()
"""