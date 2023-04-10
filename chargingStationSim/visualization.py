# -*- encoding: utf-8 -*-
"""
This file contains the visualization of simulation results.
"""

__author__ = 'Lina Grünbeck / lina.grunbeck@gmail.com'

import pandas as pd
import math
import matplotlib.pyplot as plt
# import matplotlib.dates as mdates
# plt.style.use('stylename')
from matplotlib import cycler


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


def get_data(path, runs, flex):
    results = []
    if flex:
        for run_id in range(runs):
            results.append(pd.read_csv(path + f'/simulation_{run_id}_flex.csv'))
    else:
        for run_id in range(runs):
            results.append(pd.read_csv(path + f'/simulation_{run_id}.csv'))
    data = pd.concat(results)
    data['Time'] = pd.to_datetime(data['Time'])
    return data


def station_plot(data, flexibility, iterations, path, runs):

    # Development of the station power.
    """
    multi_run = data.groupby(['RunId', 'iteration', data['Time'].dt.time])['Power'].mean()

    plt.figure()
    for run_nr in range(runs):
        for iter_num in range(iterations):
            multi_run.xs((run_nr, iter_num), level=['RunId', iteration']).plot()
    plt.show()
    """

    def make_subplots():
        if runs > 2:
            figure, axis = plt.subplots(nrows=math.ceil(runs / 2), ncols=2, layout='constrained', sharex=True, sharey=True)
            figure.set_figwidth(10)
            figure.set_figheight(8)
        else:
            figure, axis = plt.subplots(nrows=2, ncols=1, figsize=(8, 5), layout='constrained', sharex=True, sharey=True)
            figure.set_figwidth(6)
            figure.set_figheight(8)
        return figure, axis

    def plot_max(df, ax, col_name):
        """
        Plots maximum value of time series.
        """
        if col_name is not None:
            x_max = df[col_name].idxmax()
            y_max = df[col_name].max()
        else:
            x_max = df.idxmax()
            y_max = df.max()
        if ax is not None:
            ax.plot(x_max, y_max, marker='o', color='#3F5D7D')
            ax.annotate(str(round(y_max)) + 'kW',  # this is the text
                        (x_max, y_max),  # these are the coordinates to position the label
                        textcoords="offset points",  # how to position the text
                        xytext=(25, 6),  # distance from text to points (x,y)
                        ha='center',
                        color='#3F5D7D')
        else:
            plt.plot(x_max, y_max, marker='o', color='#3F5D7D')
            plt.annotate(str(round(y_max)) + 'kW',  # this is the text
                         (x_max, y_max),  # these are the coordinates to position the label
                         textcoords="offset points",  # how to position the text
                         xytext=(25, 6),  # distance from text to points (x,y)
                         ha='center',
                         color='#3F5D7D')

    # ----------------------------------------------------------------------------------------------------------------------

    if not flexibility:
        # Development of station power by vehicle type.
        type_data = data.groupby([data['RunId'], data['iteration'], data['Time'].dt.time, data['Type']])['power'].sum()
        type_data_mean = type_data.groupby(['RunId', 'Time', 'Type']).mean()
        type_mean = pd.DataFrame()
        type_mean['Internal'] = type_data_mean.xs('Internal', level='Type')
        type_mean['External'] = type_data_mean.xs('External', level='Type')

        fig, axs = make_subplots()
        for run_nr, ax in enumerate(axs.flat):
            try:
                type_mean.xs(run_nr, level='RunId').plot.area(ax=ax, stacked=False, alpha=.8)
                ax.set_title(f'Scenario {run_nr + 1})', fontweight="bold")
                ax.set_xlabel('Tid')
                ax.set_ylabel('Effekt [kW]')
            except KeyError:
                ax.grid(False)
                plt.show()
        fig.savefig(f'{path}/load_type_plot_all.pdf')
        plt.show()

    # ----------------------------------------------------------------------------------------------------------------------

        break_data = data.groupby([data['RunId'], data['iteration'], data['Time'].dt.time, data['BreakType']])[
            'power'].sum()
        break_data_mean = break_data.groupby(['RunId', 'Time', 'BreakType']).mean()
        break_mean = pd.DataFrame()
        break_mean['Internal'] = break_data_mean.xs('Internal', level='BreakType')
        break_mean['ShortBreak'] = break_data_mean.xs('ShortBreak', level='BreakType')
        break_mean['LongBreak'] = break_data_mean.xs('LongBreak', level='BreakType')

        fig, axs = make_subplots()
        for run_nr, ax in enumerate(axs.flat):
            try:
                break_mean.xs(run_nr, level='RunId').plot.area(ax=ax, alpha=.8)
                ax.set_title(f'Scenario {run_nr + 1})', fontweight="bold")
                ax.set_xlabel('Tid')
                ax.set_ylabel('Effekt [kW]')
            except KeyError:
                ax.grid(False)
                plt.show()
        fig.savefig(f'{path}/load_rest_plot_all.pdf')
        plt.show()

    # ----------------------------------------------------------------------------------------------------------------------

    """
    # Mean power and standard deviation for all runs.
    mean_data_2 = pd.DataFrame()
    mean_data_2['mean'] = data.groupby(data['Time'].dt.time)['Power'].mean()
    mean_data_2['std'] = data.groupby(data['Time'].dt.time)['Power'].std()
    mean_data_2['max'] = mean_data_2['mean'].max()
    """

    # Mean power and standard deviation for all runs.
    mean_data = pd.DataFrame()
    sum_data = data.groupby(['RunId', 'iteration', data['Time'].dt.time])['power'].sum()
    mean_data['mean'] = sum_data.groupby(['RunId', 'Time']).mean()
    mean_data['std'] = sum_data.groupby(['RunId', 'Time']).std()
    # mean_data['max'] = mean_data['mean'].max()

    """
    plt.figure()
    mean_data['mean'].plot()
    mean_data['max'].plot(linestyle='dotted', linewidth=1.5)
    # ax.xaxis.set_major_locator(HourLocator())
    plt.xlabel('Time')
    plt.ylabel('Power [kW]')
    plt.title('Station load')
    
    # plt.savefig(f'{path}/load_plot_{run_nr}.pdf')
    plt.show()
    """

    # ----------------------------------------------------------------------------------------------------------------------
    for run_nr in range(runs):
        run_data = mean_data.xs(run_nr, level='RunId')
        plt.figure()
        run_data['mean'].plot()
        plot_max(run_data, None, 'mean')
        over_line = (run_data['mean'] - run_data['std'])
        under_line = (run_data['mean'] + run_data['std'])
        plt.fill_between(run_data.index, under_line,
                         over_line, alpha=.3)
        plt.xlabel('Tid')
        plt.ylabel('Effekt [kW]')

        if flexibility:
            plt.savefig(f'{path}/mean_load_plot_{run_nr+1}_flex.pdf')
            plt.show()
        else:
            plt.savefig(f'{path}/mean_load_plot_{run_nr+1}.pdf')
            plt.show()

    fig, axs = make_subplots()
    for run_nr, ax in enumerate(axs.flat):
        try:
            run_data = mean_data.xs(run_nr, level='RunId')
            run_data['mean'].plot(ax=ax)
            plot_max(run_data, ax, 'mean')
            over_line = (run_data['mean'] - run_data['std'])
            under_line = (run_data['mean'] + run_data['std'])
            ax.fill_between(run_data.index, under_line,
                            over_line, alpha=.3)
            ax.set_title(f'Scenario {run_nr+1})', fontweight="bold")
            ax.set_xlabel('Tid')
            ax.set_ylabel('Effekt [kW]')
        except KeyError:
            # hide unused axis.
            #ax.get_xaxis().set_visible(False)
            #ax.get_yaxis().set_visible(False)
            ax.grid(False)
            plt.show()

        if flexibility:
            fig.savefig(f'{path}/mean_load_plot_all_flex.pdf')
        else:
            fig.savefig(f'{path}/mean_load_plot_all.pdf')

    # ----------------------------------------------------------------------------------------------------------------------

    if flexibility:
        for run_nr in range(runs):
            power_data = data.groupby(['RunId', 'iteration', data['Time'].dt.time])['Power'].mean()
            # power_data_mean = power_data.groupby(['Time']).mean()
            batt_data = data.groupby(['RunId', 'iteration', data['Time'].dt.time])['Batt_power'].mean()
            batt_soc = data.groupby(['RunId', 'iteration', data['Time'].dt.time, 'Type'])['Soc'].mean()

            fig, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True, gridspec_kw={'height_ratios': [2, 1, 1]})
            fig.set_figheight(8)
            # mean_data['mean'].plot(ax=ax1)
            # plot_max(mean_data, ax1, 'mean')
            power_data.xs((run_nr, 0), level=['RunId', 'iteration']).plot(ax=ax1)
            plot_max(power_data.xs((run_nr, 0), level=['RunId', 'iteration']), ax1, None)
            batt_data.xs((run_nr, 0), level=['RunId', 'iteration']).plot.area(ax=ax2, color='#07bd9c', alpha=.6,
                                                                              stacked=False)
            batt_soc.xs((run_nr, 0, 'Battery'), level=['RunId', 'iteration', 'Type']).plot(ax=ax3, color='#f5692c')
            ax2.spines[['top', 'bottom', 'left', 'right']].set_color('#444444')
            ax3.spines[['top', 'bottom', 'left', 'right']].set_color('#444444')
            ax1.set(ylabel='Effekt [kW]')
            ax2.set(ylabel='Effekt [kW]')
            ax3.set(ylabel='Soc [%]')
            ax3.set(xlabel='Tid')
            ax2.title.set_text('Stasjonært batteri')

            plt.savefig(f'{path}/flex_load_plot_{run_nr+1}.pdf')
            plt.show()

    # ----------------------------------------------------------------------------------------------------------------------

    # Boxplot for mean power over all runs.
    boxplot = pd.DataFrame()
    for run_nr in range(runs):
        boxplot[f'Scenario {run_nr+1}'] = sum_data.xs(run_nr, level='RunId')
    plt.figure()
    boxplot.plot.box()
    # plt.xlabel('Scenario nr.')
    plt.ylabel('Effekt [kW]')
    # plt.savefig(f'{path}/boxplot.pdf')
    plt.show()

    return data


def vehicle_plot(data, steps, path, runs):
    data.set_index(['iteration', 'Step'], inplace=True)

    # Start soc for all vehicles.
    """
    start_soc = data.xs((0, 0), level=['iteration', 'Step'])['Soc']
    plt.figure()
    start_soc.hist(bins=range(int(data.Soc.max()) + 1))
    plt.xlabel('SoC [%]')
    plt.ylabel('Number of vehicles')
    plt.title('Start SoC')
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
    """
    # xs() returns a specific section of the dataframe based on index level and row values.
    start_arrival = data.xs((0, 0), level=['iteration', 'Step'])['Arrival']
    plt.figure()
    start_arrival.groupby(start_arrival.dt.hour).count().plot(kind='bar')
    plt.xlabel('Time [h]')
    plt.ylabel('Number of vehicles')
    plt.title('Arrival times')
    plt.show()
    """

    # Break type for all vehicles.
    """
    break_type = data.xs((0, 140), level=['iteration', 'Step'])['BreakType']
    plt.figure()
    break_type.groupby(break_type).count().plot(kind='bar')
    plt.xlabel('Break type')
    plt.ylabel('Number of vehicles')
    plt.title('Break types')
    plt.show()
    """

    # Battery capacity for all vehicles.
    """
    capacity = data.xs((0, 0), level=['iteration', 'Step'])['Capacity']
    plt.figure()
    capacity.groupby(capacity).count().plot(kind='bar')
    plt.xlabel('Capacity [kWh]')
    plt.ylabel('Number of vehicles')
    plt.title('Battery capacity')
    plt.show()
    """

    # Max charging power for all vehicles.
    """
    charge = data.xs((0, 0), level=['iteration', 'Step'])['MaxCharge']
    plt.figure()
    charge.groupby(charge).count().plot(kind='bar')
    plt.xlabel('Power [kW]')
    plt.ylabel('Number of vehicles')
    plt.title('Max charging power')
    plt.show()
    """

    # Distribution of vehicle types.
    """
    types = data.xs((0, 0), level=['iteration', 'Step'])['Type']
    plt.figure()
    types.groupby(types).count().plot(kind='bar')
    plt.xlabel('Type')
    plt.ylabel('Number of vehicles')
    plt.title('Vehicle types')
    plt.show()
    """

    # Distribution of waiting times.
    """
    wait = data.xs((0, 143), level=['iteration', 'Step'])['Waiting']
    plt.figure()
    wait.groupby(wait).count().plot(kind='bar')
    plt.xlabel('Time [min]')
    plt.ylabel('Number of vehicles')
    plt.title('Waiting times')
    plt.show()
    """

    #
    wait = pd.DataFrame()
    wait_mean = data.groupby(['RunId', 'iteration', 'Step'])['Waiting'].mean()
    wait_mean = wait_mean.xs(steps, level='Step')
    for run_nr in range(runs):
        wait[f'Scenario {run_nr+1}'] = wait_mean.xs(run_nr, level='RunId')
    plt.figure()
    wait.plot.box()
    # plt.xlabel('Scenario nr.')
    plt.ylabel('Tid [min]')
    plt.savefig(f'{path}/waiting_plot.pdf')
    plt.show()

    return wait_mean


if __name__ == '__main__':
    sim_time = 24
    time_resolution = 10
    flexibility = True
    num_iter = 10
    runs = 3
    save_path = 'C:/Users/linag/OneDrive - Norwegian University of Life Sciences/Master/Plot'

    num_steps = int((sim_time / time_resolution) * 60) - 1
    set_plotstyle()
    data = get_data(save_path, runs, flexibility)
    # Run functions for visualization of the simulation results.
    station_data = station_plot(data, flexibility=flexibility, iterations=num_iter, path=save_path, runs=runs)
    vehicle_data = vehicle_plot(data, steps=num_steps, path=save_path, runs=runs)