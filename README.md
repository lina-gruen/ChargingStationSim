# ChargingStationSim

This repository contains a simulation framework of a charging station 
for electric trucks. 

The framework contains a model that is simulated 
with Monte Carlo-simulations. For this purpose the values for the model
parameters are drawn from probability distributions. The model 
contains chargers connected to a charging station and a fleet of 
electric trucks that visit the station. Additionally, the model contains
a local battery pack that can be connected to the station as a flexibility 
resource.

A simulation is started by running the simulation.py file after setting the
input parameters. The results can be visualized with the 
visualization.py file by specifying which files and settings should be
used.

To model the agent-based nature of the charging station model a 
modified version of the python package Mesa was used. The package files
can be found in the mesa_mod folder. batchrunner.py 
is the only file that has been modified. Since the Mesa package is under
the Apache2 license, the files in the folder are as well. All other packages
that are needed to run the model can be found in the requirements file.