# -*- encoding: utf-8 -*-
"""
This file contains visualization of simulation results.
"""

__author__ = 'Lina Grünbeck / lina.grunbeck@gmail.com'

import pandas as pd
import matplotlib.pyplot as plt
# import matplotlib.dates as mdates
# plt.style.use('stylename')
from matplotlib import cycler
# from scipy.stats import sem


def set_plotstyle():
    """
    Set custom matplotlib style.
    """
    mint = '#07bd9c'
    orange = '#f5692c'
    darkblue = '#3F5D7D'
    lightblue = '#3388BB'
    red = '#EE6666'
    purple = '#9988DD'
    lightgreen = '#88BB44'
    pink = '#FFBBBB'
    yellow = '#EECC55'
    extra_darkgrey = '#E6E6E6'
    darkgrey = '#444444'
    lightgrey = (0.92, 0.92, 0.92)
    colors = cycler('color', [darkblue, red, lightblue, purple, yellow, lightgreen, pink])
    # plt.rc('figure', facecolor=extra_darkgrey, edgecolor='none'),
    # plt.rc('axes', facecolor=extra_darkgrey, edgecolor='none',
    #        axisbelow=True, grid=True, prop_cycle=colors)
    # plt.rc('grid', color='w', linestyle='solid', linewidth=1)
    # plt.rc('xtick', direction='out', color='dimgray')
    # plt.rc('ytick', direction='out', color='dimgray')
    # plt.rc('patch', edgecolor=extra_darkgrey)
    # plt.rc('lines', linewidth=2)
    plt.rc('axes', axisbelow=True, grid=True, edgecolor='none', labelcolor=darkgrey, prop_cycle=colors)
    plt.rc('grid', color=lightgrey, linestyle='solid', linewidth=1)
    plt.rc('xtick', direction='out', color=darkgrey)
    plt.rc('ytick', direction='out', color=darkgrey)
    plt.rc('text', color=darkgrey)
    plt.rc('patch', edgecolor='#E6E6E6')
    plt.rc('lines', linewidth=2)


def station_plot(results, multirun=False, iterations=0, time_step=10/60, sim_duration=24, path=''):
    data = pd.DataFrame(results)
    # Convert 10 min resolution to hours.
    # data['Step'] *= time_step

    # If only one run is made.
    if not multirun:
        data.set_index(['Time'], inplace=True)

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

        # Mean power and standard deviation for all runs.
        mean_data = pd.DataFrame()
        mean_data['mean'] = data.groupby(data['Time'].dt.time)['Power'].mean()
        mean_data['std'] = data.groupby(data['Time'].dt.time)['Power'].std()
        mean_data['max'] = mean_data['mean'].max()

        plt.figure()
        mean_data['mean'].plot()
        mean_data['max'].plot(linestyle='dotted', linewidth=1.5)
        # ax.xaxis.set_major_locator(HourLocator())
        plt.xlabel('Time')
        plt.ylabel('Power [kW]')
        plt.title('Station load')

        plt.savefig(f'{path}/load_plot.pdf')

        plt.figure()
        over_line = (mean_data['mean'] - mean_data['std'])
        under_line = (mean_data['mean'] + mean_data['std'])
        mean_data['mean'].plot()
        plt.fill_between(mean_data.index, under_line,
                         over_line, alpha=.3)
        # ax.xaxis.set_major_locator(HourLocator())
        mean_data['max'].plot(linestyle='dotted', linewidth=1.5)
        plt.xlabel('Time')
        plt.ylabel('Power [kW]')
        plt.title('Station load')

        plt.savefig(f'{path}/mean_load_plot.pdf')
        plt.show()

        # Boxplot for mean power over all runs.
        """
        plt.figure()
        mean_data.plot.box()
        plt.show()
        """

        """
        # Duration plot for mean power over all runs.
        dur_data = mean_data
        dur_data['interval'] = time_step  # time per step in hours.
        dur_data.sort_values(by=['mean'], ascending=False, inplace=True)
        dur_data['duration'] = dur_data['interval'].cumsum()
        dur_data['percentage'] = dur_data['duration'] * 100 / sim_duration
        dur_data.set_index('percentage', inplace=True)
        reduced_dur = dur_data['mean'].drop_duplicates()
        """

        """
        plt.figure()
        reduced_dur.plot()
        plt.xlabel('Percentage [%]')
        plt.ylabel('Load [kW]')
        plt.title('Duration curve')
        plt.show()
        """

    return data


def vehicle_plot(results):
    data = pd.DataFrame(results)
    # data['Step'] *= (10/60)
    data.set_index(['iteration', 'Step'], inplace=True)

    # Start soc for all vehicles.
    """
    start_soc = data.xs((0, 0), level=['iteration', 'Step'])['Soc']
    plt.figure()
    start_soc.hist(bins=range(int(data.Soc.max()) + 1))
    plt.xlabel('SOC [%]')
    plt.ylabel('Number of vehicles')
    plt.title('Starts soc')
    plt.show()
    """

    # Final soc of all vehicles.
    """
    end_soc = data.xs(num_steps, level='Step')['Soc']
    plt.figure()
    end_soc.hist(bins=range(int(data.Soc.max()) + 1))
    plt.show()
    """

    # Development of the soc for all vehicles.
    """
    plt.figure()
    for vehicle in range(model_params['num_vehicle']):
        plt.plot(data.xs(vehicle, level='AgentID')['Soc'], marker='o', label=f'#{vehicle} soc')
        plt.legend()
        plt.show()
    """

    # Chosen arrival times for each vehicle.
    # xs() returns a specific section of the dataframe based on index level and row values.
    start_arrival = data.xs((0, 0), level=['iteration', 'Step'])['Arrival']
    plt.figure()
    start_arrival.groupby(start_arrival.dt.hour).count().plot(kind='bar')
    plt.xlabel('Time [h]')
    plt.ylabel('Number of vehicles')
    plt.title('Arrival times')
    plt.show()

    # Battery capacity for all vehicles.
    capacity = data.xs((0, 0), level=['iteration', 'Step'])['Capacity']
    plt.figure()
    capacity.groupby(capacity).count().plot(kind='bar')
    plt.xlabel('Capacity [kWh]')
    plt.ylabel('Number of vehicles')
    plt.title('Battery capacity')
    plt.show()

    # Max charging power for all vehicles.
    charge = data.xs((0, 0), level=['iteration', 'Step'])['MaxCharge']
    plt.figure()
    charge.groupby(charge).count().plot(kind='bar')
    plt.xlabel('Power [kW]')
    plt.ylabel('Number of vehicles')
    plt.title('Max charging power')
    plt.show()

    return data
