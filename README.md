# ChargingStationSim

This repository contains a simulation framework of a charging station 
for electric trucks. The framework contains a model of the charging 
station that is simulated with the Monte Carlo-simulations. For this purpose
the values for the charging station parameters are drawn 
from probability distributions.

The model contains chargers connected to the charging station and
a fleet of electric trucks that visit the station. Additionally, the
model contains a local battery pack that can be connected to the
station as a flexibility resource.

To model the agent-based nature of the charging station model a 
modified version of the python package Mesa was used. This package is 
under the Apache2 license, and the files in the mesa_mod folder of this
repository are thereby under the same license. The batchrunner.py file is the only modified 
file in the folder.