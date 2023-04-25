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
    data['Arrival'] = pd.to_datetime(data['Arrival'])
    return data


def make_subplots(share_x, share_y):
    if runs > 2:
        figure, axis = plt.subplots(nrows=math.ceil(runs / 2), ncols=2, layout='tight',
                                    sharex=share_x, sharey=share_y)
        figure.set_figwidth(10)
        figure.set_figheight(8)
    else:
        figure, axis = plt.subplots(nrows=2, ncols=1, figsize=(8, 5), layout='tight',
                                    sharex=share_x, sharey=share_y)
        figure.set_figwidth(6)
        figure.set_figheight(8)
    return figure, axis


def plot_max(df, ax, col_name, color):
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
        ax.plot(x_max, y_max, marker='o', color=color)
        ax.annotate(str(round(y_max)) + 'kW',  # this is the text
                    (x_max, y_max),  # these are the coordinates to position the label
                    textcoords="offset points",  # how to position the text
                    xytext=(25, 6),  # distance from text to points (x,y)
                    ha='center',
                    fontweight='bold',
                    color=color)
    else:
        plt.plot(x_max, y_max, marker='o', color=color)
        plt.annotate(str(round(y_max)) + 'kW',  # this is the text
                     (x_max, y_max),  # these are the coordinates to position the label
                     textcoords="offset points",  # how to position the text
                     xytext=(25, 6),  # distance from text to points (x,y)
                     ha='center',
                     color=color)


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

    # ----------------------------------------------------------------------------------------------------------------------
    if not flexibility:
        # Development of station power by vehicle type.
        type_data = data.groupby([data['RunId'], data['iteration'], data['Time'].dt.time, data['Type']])['power'].sum()
        type_data_mean = type_data.groupby(['RunId', 'Time', 'Type']).mean()
        type_mean = pd.DataFrame()
        type_mean['Interne'] = type_data_mean.xs('Internal', level='Type')
        type_mean['Eksterne'] = type_data_mean.xs('External', level='Type')

        # Plot mean type plot for each run separately.
        for run_nr in range(runs):
            plt.figure()
            type_mean.xs(run_nr, level='RunId').plot.area(stacked=False, alpha=.8)
            plt.xlabel('Tid')
            plt.ylabel('Effekt [kW]')
            fig = plt.gcf()
            fig.savefig(f'{path}/load_type_plot_{run_nr + 1}.pdf')

        fig, axs = make_subplots(share_x=True, share_y=False)
        for run_nr, ax in enumerate(axs.flat):
            try:
                # type_mean.xs(run_nr, level='RunId').plot(ax=ax)
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

        break_data = data.groupby([data['RunId'], data['iteration'], data['Time'].dt.time, data['Type'],
                                  data['BreakType']])['power'].sum()
        break_data_mean = break_data.groupby(['RunId', 'Time', 'Type', 'BreakType']).mean()
        break_mean = pd.DataFrame()
        break_mean['I1'] = break_data_mean.xs(('Internal', 'ShortBreak'), level=['Type', 'BreakType'])
        break_mean['I2'] = break_data_mean.xs(('Internal', 'MediumBreak'), level=['Type', 'BreakType'])
        break_mean['I3'] = break_data_mean.xs(('Internal', 'LongBreak'), level=['Type', 'BreakType'])
        break_mean['E1'] = break_data_mean.xs(('External', 'ShortBreak'), level=['Type', 'BreakType'])
        break_mean['E2'] = break_data_mean.xs(('External', 'LongBreak'), level=['Type', 'BreakType'])

        # Plot mean type plot for each run separately.
        for run_nr in range(runs):
            plt.figure()
            break_mean.xs(run_nr, level='RunId').plot()
            plt.xlabel('Tid')
            plt.ylabel('Effekt [kW]')
            fig = plt.gcf()
            fig.savefig(f'{path}/load_rest_plot_{run_nr + 1}.pdf')

        fig, axs = make_subplots(share_x=True, share_y=False)
        for run_nr, ax in enumerate(axs.flat):
            try:
                break_mean.xs(run_nr, level='RunId').plot(ax=ax)
                # break_mean.xs(run_nr, level='RunId').plot.area(ax=ax, stacked=False, alpha=.8)
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
    sum_data = data.groupby([data['RunId'], data['iteration'], data['Time'].dt.time])['power'].sum()
    sum_mean = sum_data.groupby(['RunId', 'Time']).mean()
    sum_std = sum_data.groupby(['RunId', 'Time']).std()
    mean_data['mean'] = sum_mean
    mean_data['std'] = sum_std
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
    # Plot mean power for each run separately.
    for run_nr in range(runs):
        run_data = mean_data.xs(run_nr, level='RunId')
        fig = plt.figure()
        run_data['mean'].plot()
        plot_max(run_data, None, 'mean', '#3F5D7D')
        over_line = (run_data['mean'] - run_data['std'])
        under_line = (run_data['mean'] + run_data['std'])
        plt.fill_between(run_data.index, under_line,
                         over_line, alpha=.3)
        plt.xlabel('Tid')
        plt.ylabel('Effekt [kW]')

        if flexibility:
            fig.savefig(f'{path}/mean_load_plot_{run_nr+1}_flex.pdf')
            #plt.show()
        else:
            fig.savefig(f'{path}/mean_load_plot_{run_nr+1}.pdf')
            #plt.show()

    # Plot mean power for all runs in one figure.
    fig, axs = make_subplots(share_x=True, share_y=False)
    for run_nr, ax in enumerate(axs.flat):
        try:
            run_data = mean_data.xs(run_nr, level='RunId')
            run_data['mean'].plot(ax=ax)
            plot_max(run_data, ax, 'mean', '#3F5D7D')
            over_line = (run_data['mean'] - run_data['std'])
            under_line = (run_data['mean'] + run_data['std'])
            ax.fill_between(run_data.index, under_line,
                            over_line, alpha=.3)
            ax.set_title(f'Scenario {run_nr+1})', fontweight='bold')
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

    # ----------------------------------------------------------------------------------------------------------------------

    # Boxplot for mean power over all runs.
    """
    boxplot = pd.DataFrame()
    for run_nr in range(runs):
        boxplot[f'Scenario {run_nr+1}'] = sum_data.xs(run_nr, level='RunId')
    fig = plt.figure()
    boxplot.plot.box()
    # plt.xlabel('Scenario nr.')
    plt.ylabel('Effekt [kW]')
    # fig.savefig(f'{path}/boxplot.pdf')
    plt.show()
    """


def battery_plot(data, flex_data, path, runs):
    power_data = data.groupby(['RunId', 'iteration', data['Time'].dt.time])['Power'].mean()
    power_flex = flex_data.groupby(['RunId', 'iteration', flex_data['Time'].dt.time])['Power'].mean()
    # power_data_mean = power_data.groupby(['Time']).mean()
    batt_data = flex_data.groupby(['RunId', 'iteration', flex_data['Time'].dt.time])['Batt_power'].mean()
    batt_soc = flex_data.groupby(['RunId', 'iteration', flex_data['Time'].dt.time, 'Type'])['Soc'].mean()
    for run_nr in range(runs):
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True, gridspec_kw={'height_ratios': [2, 1, 1]})
        fig.set_figheight(8)
        # mean_data['mean'].plot(ax=ax1)
        # plot_max(mean_data, ax1, 'mean')
        # Plot power development with and without flexibility.
        power_data.xs((run_nr, 0), level=['RunId', 'iteration']).plot(ax=ax1, color='#3F5D7D', label='Uten batteri')
        plot_max(power_data.xs((run_nr, 0), level=['RunId', 'iteration']), ax1, None, '#3F5D7D')
        power_flex.xs((run_nr, 0), level=['RunId', 'iteration']).plot(ax=ax1, color='#EE6666', label='Med batteri')
        plot_max(power_flex.xs((run_nr, 0), level=['RunId', 'iteration']), ax1, None, '#EE6666')
        # Plot power development for battery.
        batt_data.xs((run_nr, 0), level=['RunId', 'iteration']).plot.area(ax=ax2, color='#07bd9c', alpha=.6,
                                                                          stacked=False)
        # Plot battery SoC development.
        batt_soc.xs((run_nr, 0, 'Battery'), level=['RunId', 'iteration', 'Type']).plot(ax=ax3, color='#f5692c')

        ax2.spines[['top', 'bottom', 'left', 'right']].set_color('#444444')
        ax3.spines[['top', 'bottom', 'left', 'right']].set_color('#444444')
        ax1.set(ylabel='Effekt [kW]')
        ax1.legend()
        fig.suptitle('Ladestasjon', fontweight='bold')
        ax2.set(ylabel='Effekt [kW]')
        ax3.set(ylabel='Soc [%]')
        ax3.set(xlabel='Tid')
        ax2.set_title('Stasjonært batteri', fontweight='bold')

        fig.savefig(f'{path}/flex_load_plot_{run_nr+1}.pdf')
        plt.show()


def vehicle_plot(data, steps, iters, runs, path):
    # data.set_index(['iteration', 'Step'], inplace=True)

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
    arrival_data = data.set_index(['RunId', 'iteration', 'Step', 'Type'])
    for run_nr in range(runs):
        start_arrival = arrival_data.xs((run_nr, 0, 0, 'External'), level=['RunId', 'iteration', 'Step', 'Type'])['Arrival']
        plt.figure()
        start_arrival.groupby([start_arrival.dt.hour]).count().plot(kind='bar')
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

    # Distribution of how many external leave the station before charging.
    charged = data.groupby(['RunId', 'iteration', 'Step', 'Type'])['Charged'].sum()
    charged_mean = charged.groupby(['RunId', 'Step', 'Type']).mean()
    charged_mean = round(charged_mean.xs((steps, 'External'), level=['Step', 'Type']), 0)
    fig = plt.figure()
    charged_mean.plot(kind='bar')
    plt.xlabel('Time [min]')
    plt.ylabel('Antall kjøretøy')
    plt.title('Antall externe som ikke ladet')
    fig.savefig(f'{path}/left_plot.pdf')
    plt.show()

    # Distribution of waiting times for all scenarios.

    wait_mean = data.groupby(['RunId', 'iteration', 'Step', 'Type'])['Waiting'].mean()
    wait_mean = wait_mean.xs(steps, level='Step')
    fig, axs = make_subplots(share_x=False, share_y=False)
    for run_nr, ax in enumerate(axs.flat):
        try:
            wait = pd.DataFrame()
            wait[f'Scenario {run_nr + 1}\ninterne'] = wait_mean.xs((run_nr, 'Internal'), level=['RunId', 'Type'])
            wait[f'Scenario {run_nr + 1}\neksterne'] = wait_mean.xs((run_nr, 'External'), level=['RunId', 'Type'])
            wait.plot.box(ax=ax)
            ax.set_ylabel('Tid [min]')
            ax.set_title(f'Scenario {run_nr + 1})', fontweight="bold")
        except KeyError:
            ax.grid(False)
            plt.show()
    # fig, axs = plt.subplots()
    # fig.set_figwidth(8)
    # wait[f'Scenario {run_nr + 1} \n interne'] = wait_mean.xs((run_nr, 'Internal'), level=['RunId', 'Type'])
    # wait[f'Scenario {run_nr + 1} \n eksterne'] = wait_mean.xs((run_nr, 'External'), level=['RunId', 'Type'])
    # wait.plot.box(ax=axs)
    fig.tight_layout(w_pad=0.5, h_pad=1.0)
    fig.savefig(f'{path}/waiting_plot.pdf')
    plt.show()


if __name__ == '__main__':
    time_resolution = 2
    num_iter = 100
    runs = 1
    flexibility = False
    plot_battery = False
    save_path = 'C:/Users/linag/OneDrive - Norwegian University of Life Sciences/Master/Plot'

    num_steps = int((24 / time_resolution) * 60) - 1
    set_plotstyle()
    data = get_data(save_path, runs, flexibility)
    # Run functions for visualization of the simulation results.
    station_plot(data, flexibility=flexibility, iterations=num_iter, path=save_path, runs=runs)
    vehicle_plot(data, steps=num_steps, iters=num_iter, runs=runs, path=save_path)
    if plot_battery and flexibility:
        without_flex = get_data(save_path, runs, False)
        battery_plot(without_flex, data, save_path, runs)
    elif plot_battery and not flexibility:
        with_flex = data = get_data(save_path, runs, True)
        battery_plot(data, with_flex, save_path, runs)
