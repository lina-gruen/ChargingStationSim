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
sim_time = 2
# Time resolution of each step in the simulation in minutes.
time_step = 10
# Number of steps the simulation requires.
num_steps = int((sim_time/time_step)*60)

# Set model parameters for a simulation.
model_params = {'num_vehicle': 6, 'num_battery': 0, 'num_charger': 2, 'time_step': time_step}

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
results_df = pd.DataFrame(results)
results_df.set_index(['Step', 'AgentID'], inplace=True)

# Find final soc of all vehicles.
end_soc = results_df.xs(num_steps, level="Step")["Soc"]

plt.figure()
end_soc.hist(bins=range(int(results_df.Soc.max()) + 1))
# plt.show()

# Plot development of the soc of some vehicles.
plt.figure()
plt.plot(results_df.xs(3, level='AgentID')['Soc'], marker='o', label='Vehicle 3 soc')
plt.plot(results_df.xs(5, level='AgentID')['Soc'], marker='o', label='Vehicle 5 soc')
plt.legend()
plt.show()