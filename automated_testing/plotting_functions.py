import math
import matplotlib.pyplot as plt
import numpy as np

"""
    Plotting Functions:
    This file includes all plotting variants used in the automated testing
"""


def plot_data(df, min_nodes, max_nodes, problems, squeezed):
    problem_hardness = []
    for problem in problems:
        problem_hardness.append(sum(problem.param_fragment_size))
    avg_problem_hardness = np.mean(problem_hardness)
    y_axises = ['time', 'deviation', 'space']
    for y_axis in y_axises:
        fig, ax = plt.subplots()
        ax.set(xlabel='Node Count', ylabel=y_axis, title=f'Average {y_axis} per node count')
        if y_axis == 'space':
            for node_count in range(min_nodes,max_nodes+1):
                df = df.append({'algo':'Total Replication', 'space':(avg_problem_hardness*node_count), 'nodes':node_count, 'time':0, 'deviation':0, 'total_replication':0}, ignore_index=True)
        plot_group = df.groupby(['algo', 'nodes'], as_index=False)[y_axis].mean().groupby('algo')
        for name, group in plot_group:
            group.plot(x='nodes', y=y_axis, label=name, ax=ax)
        plt.xticks([i for i in range(min_nodes, max_nodes + 1)])
        plt.show()
    df = df[df.algo != "Total Replication"]
    deviation = ((df.groupby('algo').mean() / df.groupby('algo').mean().loc['Complete']) - 1) * 100
    deviation = deviation.drop(columns=['nodes'])
    if squeezed:
        deviation = deviation.drop(columns=['deviation'])
    fig, ax = plt.subplots()
    deviation.plot.bar(ax=ax)
    ax.set(xlabel='Split Strategies', ylabel='%',
           title='%-Deviation from optimum Complete Split Strategy')
    plt.show()


def plot_heu_vs_opt(df, min_nodes, max_nodes, problems, squeezes):
    problem_hardness = []
    for problem in problems:
        problem_hardness.append(sum(problem.param_fragment_size))
    avg_problem_hardness = np.mean(problem_hardness)
    y_axises = ['time', 'deviation', 'space']
    for y_axis in y_axises:
        fig, ax = plt.subplots()
        ax.set(xlabel='Node Count', ylabel=y_axis, title=f'Average {y_axis} per node count')
        if y_axis == 'space':
            for node_count in range(min_nodes, max_nodes + 1):
                df = df.append(
                    {'algo': 'Total Replication', 'space': (avg_problem_hardness * node_count),
                     'nodes': node_count, 'time': 0, 'deviation': 0, 'total_replication': 0},
                    ignore_index=True)
        plot_group = df.groupby(['algo', 'nodes'], as_index=False)[y_axis].mean().groupby('algo')
        for name, group in plot_group:
            group.plot(x='nodes', y=y_axis, label=name, ax=ax)
        plt.xticks([i for i in range(min_nodes, max_nodes + 1)])
        plt.show()
    df = df[df.algo != "Total Replication"]
    deviation = ((df.groupby('algo').mean() / df.groupby('algo').mean().loc['Complete']) - 1) * 100
    deviation = deviation.drop(index=['Complete'])
    deviation = deviation.drop(columns=['nodes', 'total_replication'])
    if not squeezes:
        deviation = deviation.drop(columns=[ 'deviation'])

    fig, ax = plt.subplots()
    deviation.plot.bar(ax=ax)
    ax.set(xlabel='Split Strategies', ylabel='%',
           title='%-Difference from optimum complete split')
    plt.show()


def plot_data_pareto(df):
    plot_group = df.groupby(['algo', 'epsilon'], as_index=False).mean()
    for algo in plot_group['algo'].unique():
        fig, axs = plt.subplots(1, 3, figsize=(10, 3))
        axs[0].set(xlabel='Space', ylabel='Deviation', title=f'Space / Deviation for {algo}')
        color = plot_group[plot_group.algo == algo]['epsilon'].apply(lambda x: math.log(x, 10))
        plot_group[plot_group.algo == algo].plot.scatter(x='space',
                                                         y='deviation',
                                                         ax=axs[0],
                                                         colormap='cool',
                                                         c=color)
        axs[1].set(xlabel='Space', ylabel='Deviation', title=f'Time / Deviation for {algo}')
        plot_group[plot_group.algo == algo].plot.scatter(x='time',
                                                         y='deviation',
                                                         ax=axs[1],
                                                         colormap='cool',
                                                         c=color)
        axs[2].set(xlabel='Space', ylabel='Deviation', title=f'Space / Time for {algo}')
        plot_group[plot_group.algo == algo].plot.scatter(x='time',
                                                         y='space',
                                                         ax=axs[2],
                                                         colormap='cool',
                                                         c=color)
        plt.tight_layout()
        plt.show()


def plot_data_timeout(df):
    plot_group = df.groupby(['algo', 'timeout'], as_index=False).mean()
    for algo in plot_group['algo'].unique():
        fig, axs = plt.subplots(1, 3, figsize=(10, 3))
        axs[0].set(xlabel='Timeout', ylabel='Space', title='Space / Timeout Relation')
        plot_group[plot_group.algo == algo].plot.scatter(x='timeout',
                                                         y='space',
                                                         ax=axs[0])
        axs[1].set(xlabel='Timeout', ylabel='Time', title='Time / Timeout Relation')
        plot_group[plot_group.algo == algo].plot.scatter(x='timeout',
                                                         y='time',
                                                         ax=axs[1])
        axs[2].set(xlabel='Timeout', ylabel='Deviation', title='Deviation / Timeout Relation')
        plot_group[plot_group.algo == algo].plot.scatter(x='timeout',
                                                         y='deviation',
                                                         ax=axs[2])
        plt.tight_layout()
        plt.show()