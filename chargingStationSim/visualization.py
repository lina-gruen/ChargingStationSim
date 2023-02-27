# -*- encoding: utf-8 -*-
"""
This file contains visualization of simulation results.
"""

__author__ = 'Lina Grünbeck / lina.grunbeck@gmail.com'

import pandas as pd
import matplotlib.pyplot as plt


def station_plot(results, multirun=False, iterations=0, resolution=60/10, sim_duration=24):
    data = pd.DataFrame(results)
    # Convert 10 min resolution to hours.
    data['Step'] *= (10/60)

    # If only one run is made.
    if not multirun:
        data.set_index(['Step'], inplace=True)

        # Development of the station power.
        plt.figure()
        plt.plot(data.xs('Power', axis=1))
        plt.xlabel('Time [h]')
        plt.ylabel('Power [kW]')
        plt.title('Station power')
        plt.show()
    # If multiple runs are made, the mean of all runs is plotted.
    else:
        data.set_index(['iteration', 'Step'], inplace=True)

        # Development of the station power.
        """
        plt.figure()
        for iter_num in range(iterations):
            plt.plot(data.xs(iter_num, level='iteration')['Power'])
        """

        # Dataframe with mean power for all runs.
        mean_data = pd.DataFrame()
        mean_data['load'] = data.groupby('Step')['Power'].mean()

        plt.figure()
        plt.plot(mean_data)
        plt.xlabel('Time [h]')
        plt.ylabel('Power [kW]')
        plt.title('Station power')
        plt.show()

        # Boxplot for mean power over all runs.
        """
        plt.figure()
        mean_data.plot.box()
        plt.show()
        """

        # Duration plot for mean power over all runs.
        mean_data['interval'] = resolution  # time per step in hours.
        mean_data.sort_values(by=['load'], ascending=False, inplace=True)
        mean_data['duration'] = mean_data['interval'].cumsum()
        mean_data['percentage'] = mean_data['duration'] * 100 / sim_duration
        mean_data.set_index('percentage', inplace=True)
        reduced_mean = mean_data['load'].drop_duplicates()

        plt.figure()
        reduced_mean.plot()
        plt.xlabel('Percentage [%]')
        plt.ylabel('Load [kW]')
        plt.title('Duration curve')
        plt.show()

    return data


def vehicle_plot(results):
    data = pd.DataFrame(results)
    data['Step'] *= (10/60)
    data.set_index(['Step', 'AgentID'], inplace=True)

    # Start soc for all vehicles.
    start_soc = data.xs(0, level='Step')['Soc']
    plt.figure()
    start_soc.hist(bins=range(int(data.Soc.max()) + 1))
    plt.xlabel('Time [min/10]')
    plt.ylabel('Number of vehicles')
    plt.title('Starts soc')
    plt.show()

    # Final soc of all vehicles.
    """
    end_soc = data.xs(num_steps, level='Step')['Soc']
    plt.figure()
    end_soc.hist(bins=range(int(data.Soc.max()) + 1))
    plt.show()
    """

    # Chosen arrival times for each vehicle.
    # xs() returns a specific section of the dataframe based on index level and row values.
    start_arrival = data.xs(0, level='Step')['Arrival']
    plt.figure()
    start_arrival.hist(bins=range(int(data.Arrival.max()) + 1))
    plt.xlabel('Time [min/10]')
    plt.ylabel('Number of vehicles')
    plt.title('Arrival times')
    plt.show()

    # Development of the soc for all vehicles.
    """
    plt.figure()
    for vehicle in range(model_params['num_vehicle']):
        plt.plot(data.xs(vehicle, level='AgentID')['Soc'], marker='o', label=f'#{vehicle} soc')
        plt.legend()
        plt.show()
    """

    return data
