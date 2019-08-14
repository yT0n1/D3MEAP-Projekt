import random
import os
import sys
from datetime import datetime

import math
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd

from playground import Problem
from solver_node import solve_for_tree
from tree_generation import one_split_tree, one_vs_all_split, approximate_tree, prime_factor_tree

import numpy as np

mpl.rcParams['figure.dpi'] = 400


def generate_queries(num_queries, num_fragments):
    queries = []
    for i in range(num_queries):
        temp_list = []
        for j in range(num_fragments):
            temp_list.append(random.choice([0, 1]))
        queries.append(temp_list)
    return queries


def automated_test():
    # Configuration
    min_nodes = 3
    max_nodes = 6
    timeout = 15
    num_problems = 3
    should_squeeze = False
    epsilon_factor = 10000

    problems = generate_problems(num_problems)

    # total_results, df = test_with_nodes(min_nodes, max_nodes, problems, timeout, should_squeeze, epsilon_factor)
    #total_results, df = test_with_nodes(min_nodes, max_nodes, problems, timeout, should_squeeze, epsilon_factor)
    #plot_data(df, min_nodes, max_nodes)

    selected_node_count = 12
    #pareto_results, df = epsilon_pareto_front(selected_node_count, problems, timeout)
    #plot_data_pareto(df)

    timeout_results, df = timeout_tests(selected_node_count, problems)
    plot_data_timeout(df)

    df.to_csv("out.csv")


def test_2_2():
    problem1 = Problem()

def test_with_nodes(min_nodes, max_nodes, problems, timeout, should_squeeze, epsilon_factor):
    total_results = []
    df = pd.DataFrame(columns=['nodes', 'algo', 'time', 'space', 'deviation'])

    for node_count in range(min_nodes, max_nodes + 1):
        epoch_results = []
        for problem in problems:
            print(f"\n SOLVING: NODE COUNT { node_count }, PROBLEM { problems.index(problem) } AT { str(datetime.now()) }")
            # s1 = solve_for_tree(one_split_tree(node_count), problem, timeout)
            sys.stdout = open(os.devnull, "w")
            s11 = solve_for_tree(one_split_tree(node_count), problem, timeout, should_squeeze,
                                 epsilon_factor)

            s2 = solve_for_tree(prime_factor_tree(node_count, False, False), problem, timeout,
                                should_squeeze, epsilon_factor)
            s3 = solve_for_tree(prime_factor_tree(node_count, True, False), problem, timeout,
                                should_squeeze, epsilon_factor)

            s4 = solve_for_tree(one_vs_all_split(node_count), problem, timeout, should_squeeze,
                                epsilon_factor)

            s5 = solve_for_tree(approximate_tree(node_count, 2), problem, timeout, should_squeeze,
                                epsilon_factor)
            s6 = solve_for_tree(approximate_tree(node_count, 3), problem, timeout, should_squeeze,
                                epsilon_factor)
            s7 = solve_for_tree(approximate_tree(node_count, 4), problem, timeout, should_squeeze,
                                epsilon_factor)
            s8 = solve_for_tree(approximate_tree(node_count, 5), problem, timeout, should_squeeze,
                                epsilon_factor)
            s9 = solve_for_tree(approximate_tree(node_count, 6), problem, timeout, should_squeeze,
                                epsilon_factor)
            s10 = solve_for_tree(approximate_tree(node_count, 7), problem, timeout, should_squeeze,
                                 epsilon_factor)
            sys.stdout = sys.__stdout__

            xx_results = [s2, s3, s4, s5, s6, s7, s8, s9, s10, s11]
            for res in xx_results:
                # The name is split due to the very verbose and varying naming for prime trees
                df.loc[len(df)] = [node_count, res.name.split('|')[0], res.time, res.space,
                                   res.deviation]
            # for xx_r in xx_results:
            # dot_export_actual_workload(xx_r.tree)
            epoch_results.append(xx_results)
        total_results.append(epoch_results)
    # unfortunately we have to enforce the column types manually or some will be object which
    # will break aggregation.
    df.nodes = df.nodes.astype('int')
    df.algo = df.algo.astype('str')
    df.time = df.time.astype('float')
    df.space = df.space.astype('int')
    df.deviation = df.deviation.astype('float')
    return total_results, df


def epsilon_pareto_front(selected_node_count, problems, timeout):
    total_results = []
    df = pd.DataFrame(columns=['epsilon', 'algo', 'time', 'space', 'deviation'])
    epsilon_factor_array = [10, 100, 1000, 3000, 5000, 7500, 10000, 500000, 1000000]

    for epsilon_factor in epsilon_factor_array:
        epoch_results = []
        for problem in problems:
            # s1 = solve_for_tree(one_split_tree(node_count), problem, timeout)
            s11 = solve_for_tree(one_split_tree(selected_node_count), problem, timeout, True,
                                 epsilon_factor)

            s2 = solve_for_tree(prime_factor_tree(selected_node_count, False, False), problem,
                                timeout, True, epsilon_factor)
            s3 = solve_for_tree(prime_factor_tree(selected_node_count, True, False), problem,
                                timeout, True, epsilon_factor)

            s4 = solve_for_tree(one_vs_all_split(selected_node_count), problem, timeout, True,
                                epsilon_factor)

            s5 = solve_for_tree(approximate_tree(selected_node_count, 2), problem, timeout, True,
                                epsilon_factor)
            s6 = solve_for_tree(approximate_tree(selected_node_count, 3), problem, timeout, True,
                                epsilon_factor)
            s7 = solve_for_tree(approximate_tree(selected_node_count, 4), problem, timeout, True,
                                epsilon_factor)
            s8 = solve_for_tree(approximate_tree(selected_node_count, 5), problem, timeout, True,
                                epsilon_factor)
            s9 = solve_for_tree(approximate_tree(selected_node_count, 6), problem, timeout, True,
                                epsilon_factor)
            s10 = solve_for_tree(approximate_tree(selected_node_count, 7), problem, timeout, True,
                                 epsilon_factor)

            xx_results = [s2, s3, s4, s5, s6, s7, s8, s9, s10, s11]
            for res in xx_results:
                # The name is split due to the very verbose and varying naming for prime trees
                df.loc[len(df)] = [epsilon_factor, res.name.split('|')[0], res.time, res.space,
                                   res.deviation]

            # for xx_r in xx_results:
            # dot_export_actual_workload(xx_r.tree)
            epoch_results.append(xx_results)
        total_results.append(epoch_results)
    # unfortunately we have to enforce the column types manually or some will be object which
    # will break aggregation.
    df.epsilon = df.epsilon.astype('int')
    df.algo = df.algo.astype('str')
    df.time = df.time.astype('float')
    df.space = df.space.astype('int')
    df.deviation = df.deviation.astype('float')
    return total_results, df

def timeout_tests(selected_node_count, problems):
    total_results = []
    df = pd.DataFrame(columns=['timeout', 'algo', 'time', 'space', 'deviation'])
    timout_array = np.arange(20)

    for timeout in timout_array:
        epoch_results = []
        for problem in problems:
            # s1 = solve_for_tree(one_split_tree(node_count), problem, timeout)
            s1 = solve_for_tree(one_split_tree(selected_node_count), problem, timeout, True, 1000000)

            xx_results = [s1]
            for res in xx_results:
                # The name is split due to the very verbose and varying naming for prime trees
                df.loc[len(df)] = [timeout, res.name.split('|')[0], res.time, res.space,
                                   res.deviation]

            # for xx_r in xx_results:
            # dot_export_actual_workload(xx_r.tree)
            epoch_results.append(xx_results)
        total_results.append(epoch_results)
    # unfortunately we have to enforce the column types manually or some will be object which
    # will break aggregation.
    df.timeout = df.timeout.astype('int')
    df.algo = df.algo.astype('str')
    df.time = df.time.astype('float')
    df.space = df.space.astype('int')
    df.deviation = df.deviation.astype('float')
    return total_results, df


def generate_problems(num_epochs):
    problems = []
    for epoch in range(num_epochs):
        param_num_fragments = random.sample(range(200, 300), 1)[0]
        param_num_queries = random.sample(range(10, 25), 1)[0]

        problem = add_problem_properties(param_num_fragments, param_num_queries, 3)

        problems.append(problem)
    return problems


def add_problem_properties(param_num_fragments, param_num_queries, workloads):
    param_fragment_size = random.choices(range(1, 100), k=param_num_fragments)
    param_queries = generate_queries(param_num_queries, param_num_fragments)
    param_query_frequency = [random.choices(range(1, 100), k=param_num_queries)
                             for _ in range(workloads)]
    param_query_cost = random.choices(range(1, 100), k=param_num_queries)
    param_query_ids = [i for i in range(len(param_query_cost))]
    problem = Problem(param_fragment_size, param_queries,
                      param_query_frequency, param_query_cost, param_query_ids,
                      len(param_query_ids))
    return problem


def plot_data(df, min_nodes, max_nodes):
    y_axises = ['time', 'space', 'deviation']
    for y_axis in y_axises:
        fig, ax = plt.subplots()
        ax.set(xlabel='Node Count', ylabel=y_axis, title=f'Average {y_axis} per node count')
        plot_group = df.groupby(['algo', 'nodes'], as_index=False)[y_axis].mean().groupby('algo')
        for name, group in plot_group:
            group.plot(x='nodes', y=y_axis, label=name, ax=ax)
        plt.xticks([i for i in range(min_nodes, max_nodes + 1)])
        plt.show()

    deviation = ((df.groupby('algo').mean() / df.groupby('algo').mean().loc['Complete']) - 1) * 100
    deviation = deviation.drop(columns=['nodes'])
    fig, ax = plt.subplots()
    deviation.plot.bar(ax=ax)
    ax.set(xlabel='Split Strategies', ylabel='%',
           title='%-Deviation from optimum One Split Strategy')
    plt.show()

def plot_data_pareto(df):
    plot_group = df.groupby(['algo', 'epsilon'], as_index=False).mean()
    for algo in plot_group['algo'].unique():
        fig, axs = plt.subplots(1, 3, figsize=(10,3))
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
        plot_group[plot_group.algo == algo].plot.scatter(x='space',
                                                         y='time',
                                                         ax=axs[2],
                                                         colormap='cool',
                                                         c=color)
        plt.tight_layout()
        plt.show()

def plot_data_timeout(df):
    plot_group = df.groupby(['algo', 'timeout'], as_index=False).mean()
    for algo in plot_group['algo'].unique():
        fig, axs = plt.subplots(1, 3, figsize=(10,3))
        axs[0].set(xlabel='Timeout', ylabel='Space', title='Space / TImeout Relation')
        plot_group[plot_group.algo == algo].plot.scatter(x='timeout',
                                                         y='space',
                                                         ax=axs[0])
        axs[1].set(xlabel='Timeout', ylabel='Time', title='Time / TImeout Relation')
        plot_group[plot_group.algo == algo].plot.scatter(x='timeout',
                                                         y='time',
                                                         ax=axs[1])
        axs[2].set(xlabel='Timeout', ylabel='Deviation', title='Deviation / TImeout Relation')
        plot_group[plot_group.algo == algo].plot.scatter(x='timeout',
                                                         y='deviation',
                                                         ax=axs[2])
        plt.tight_layout()
        plt.show()


if __name__ == '__main__':
    automated_test()
