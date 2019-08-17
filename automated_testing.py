import os
import random
import sys
from datetime import datetime

import math
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from playground import Problem
from solver_node import solve_for_tree
from tree_generation import one_split_tree, one_vs_all_split, approximate_tree, prime_factor_tree, \
    dot_export_actual_workload

mpl.rcParams['figure.dpi'] = 400


def generate_queries(num_queries, num_fragments):
    queries = []
    used = [0] * num_fragments
    for q in range(num_queries - 1):
        nr_frag = np.random.binomial(num_fragments - 1, 0.3) + 1
        chosen_fragments = np.random.choice(num_fragments, nr_frag, replace=False)
        for fragment in chosen_fragments:
            used[fragment] = 1
        queries.append([1 if i in chosen_fragments else 0 for i in range(num_fragments)])
    used[0] = 0  # to avoid empty
    queries.append([0 if u else 1 for u in used])
    return queries


def automated_test():
    # df = test_2_2()
    # exit()
    # What do you want to test?
    test_node_count = False
    test_pareto = False
    test_timeout = False
    compare_lp_heuristic = True

    # General Configuration for the Problems
    num_problems = 3
    min_fragments = 20
    max_fragments = 50
    min_queries = 5
    max_queries = 10
    num_workloads = 3

    # Configuration Node Count
    NODES_min_nodes = 2
    NODES_max_nodes = 10
    NODES_timeout = 15
    NODES_should_squeeze = False
    NODES_epsilon_factor = 400000

    # Configuration Pareto Frontier
    PARETO_selected_node_count = 12
    PARETO_timeout = 15
    PARETO_epsilon_factor_array = [10, 100, 1000, 3000, 5000, 7500, 10000, 500000, 1000000]

    # Configuration Timeout Behaviour
    TIMEOUT_selected_node_count = 12
    TIMEOUT_maximum_timeout = 10
    TIMEOUT_should_squeeze = False
    TIMEOUT_epsilon_factor = 10000

    problems = generate_problems(num_problems, min_fragments, max_fragments, min_queries,
                                 max_queries, num_workloads)
    df = None

    if test_node_count:
        total_results, df = test_with_nodes(problems,
                                            NODES_min_nodes,
                                            NODES_max_nodes,
                                            NODES_timeout,
                                            NODES_should_squeeze,
                                            NODES_epsilon_factor)
        plot_data(df, NODES_min_nodes, NODES_max_nodes, problems)
        df.to_csv("test_node_out_NOEP.csv")
        total_results, df = test_with_nodes(problems,
                                            NODES_min_nodes,
                                            NODES_max_nodes,
                                            NODES_timeout,
                                            not NODES_should_squeeze,
                                            NODES_epsilon_factor)
        plot_data(df, NODES_min_nodes, NODES_max_nodes, problems)
        df.to_csv("test_node_out_EP.csv")
    if test_pareto:
        pareto_results, df = epsilon_pareto_front(problems,
                                                  PARETO_selected_node_count,
                                                  PARETO_timeout,
                                                  PARETO_epsilon_factor_array)
        plot_data_pareto(df)
        df.to_csv("data_pareto_out.csv")
    if test_timeout:
        timeout_results, df = timeout_tests(problems,
                                            TIMEOUT_selected_node_count,
                                            TIMEOUT_maximum_timeout,
                                            TIMEOUT_should_squeeze,
                                            TIMEOUT_epsilon_factor)
        plot_data_timeout(df)
        df.to_csv("test_timeout_out.csv")
    if compare_lp_heuristic:
        compare_res, df = timeout_vs_heuristic_tests(problems, NODES_min_nodes, NODES_max_nodes)
        df.to_csv("test_heu_out.csv")
        plot_heu_vs_opt(df, NODES_min_nodes, NODES_max_nodes, problems)



def test_2_2():
    sizes = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    nodes = sizes
    fragments = sizes
    queries = sizes
    df = pd.DataFrame(columns=['nodes', 'algo', 'time', 'query', 'fragment', 'space', 'deviation'])
    df.nodes = df.nodes.astype('int')
    df.algo = df.algo.astype('str')
    df.fragment = df.time.astype('int')
    df.space = df.space.astype('int')
    df.query = df.deviation.astype('int')
    for _ in range(6):
        for fragment in fragments:
            for query in queries:
                problem = add_problem_properties(fragment, query, 1)
                for node in nodes:
                    s = solve_for_tree(one_split_tree(node), problem, 900, False, 0)
                    df.loc[len(df)] = [node, s.name.split('|')[0], s.time, query, fragment, s.space,
                                       s.deviation]
    df.to_csv('test22', index=False)
    n = df.groupby('nodes', as_index=False).mean()
    q = df.groupby('query', as_index=False).mean()
    f = df.groupby('fragment', as_index=False).mean()
    fig, ax = plt.subplots()
    n.plot(y='time', x='nodes', ax=ax, label='#nodes')
    q.plot(y='time', x='query', ax=ax, label='#queries')
    f.plot(y='time', x='fragment', ax=ax, label='#fragments')
    ax.set(xlabel='', ylabel='average time in s',
           title='average runtime for factors')
    plt.xticks(sizes)
    plt.show()
    return df


def test_with_nodes(problems, min_nodes, max_nodes, timeout, should_squeeze, epsilon_factor):
    total_results = []
    df = pd.DataFrame(columns=['nodes', 'algo', 'time', 'space', 'deviation', 'total_replication'])

    for node_count in range(min_nodes, max_nodes + 1):
        epoch_results = []
        for problem in problems:
            total_replication = sum(problem.param_fragment_size) * node_count
            print(
                f"\n SOLVING: NODE COUNT {node_count}, PROBLEM {problems.index(problem)} AT {str(datetime.now())}, MAX SIZE {total_replication}")

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
                                   res.deviation, res.total_replication]
            # for xx_r in xx_results:
            #     dot_export_actual_workload(xx_r.tree)
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


def epsilon_pareto_front(problems, selected_node_count, timeout, epsilon_factor_array):
    total_results = []
    df = pd.DataFrame(columns=['epsilon', 'algo', 'time', 'space', 'deviation'])

    for epsilon_factor in epsilon_factor_array:
        epoch_results = []
        for problem in problems:
            # s1 = solve_for_tree(one_split_tree(node_count), problem, timeout)
            print(
                f"\n SOLVING: EPSILON FAC {epsilon_factor}, PROBLEM {problems.index(problem)} AT {str(datetime.now())}")
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


def timeout_vs_heuristic_tests(problems, min_node, max_node):
    total_results = []
    df = pd.DataFrame(columns=['algo', 'time', 'space', 'deviation', 'nodes'])
    should_squeeze = False
    epsilon_factor = None
    for node in range(min_node, max_node + 1):
        for problem in problems:

            s1 = solve_for_tree(approximate_tree(node, 2), problem, 900,
                                should_squeeze, epsilon_factor)
            s2 = solve_for_tree(one_split_tree(node), problem, s1.time,
                                should_squeeze, epsilon_factor)
            s3 = solve_for_tree(one_vs_all_split(node), problem, 900,
                                should_squeeze, epsilon_factor)
            s4 = solve_for_tree(one_split_tree(node), problem, s3.time,
                                should_squeeze, epsilon_factor)
            s5 = solve_for_tree(one_split_tree(node), problem, 900,
                                should_squeeze, epsilon_factor)
            s2.name = 'LP with 2-Approx timeout'
            s4.name = 'LP with One-vs-all timeout'
            xx_results = [s1, s2, s3, s4, s5]
            for res in xx_results:
                # The name is split due to the very verbose and varying naming for prime trees
                df.loc[len(df)] = [res.name.split('|')[0], res.time, res.space,
                                   res.deviation, node]

            # for xx_r in xx_results:
            # dot_export_actual_workload(xx_r.tree)
            total_results.append(xx_results)
    # unfortunately we have to enforce the column types manually or some will be object which
    # will break aggregation.
    df.algo = df.algo.astype('str')
    df.time = df.time.astype('float')
    df.space = df.space.astype('int')
    df.deviation = df.deviation.astype('float')
    df.nodes = df.nodes.astype('int')
    return total_results, df


def timeout_tests(problems, selected_node_count, maximum_timeout, should_squeeze, epsilon_factor):
    total_results = []
    df = pd.DataFrame(columns=['timeout', 'algo', 'time', 'space', 'deviation'])
    timout_array = np.arange(1, maximum_timeout)

    for timeout in timout_array:
        epoch_results = []
        for problem in problems:
            print(
                f"\n SOLVING: TIMEOUT {timeout}, PROBLEM {problems.index(problem)} AT {str(datetime.now())}")
            # s1 = solve_for_tree(one_split_tree(node_count), problem, timeout)
            s1 = solve_for_tree(one_split_tree(selected_node_count), problem, timeout,
                                should_squeeze, epsilon_factor)
            s2 = solve_for_tree(one_split_tree(selected_node_count), problem, timeout, True,
                                epsilon_factor)
            s1.name = "OneSplitNoEP"
            s2.name = "OneSplitWithEP"
            xx_results = [s1, s2]
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


def generate_problems(num_epochs, min_fragments, max_fragments, min_queries, max_queries,
                      num_workloads):
    problems = []
    for epoch in range(num_epochs):
        param_num_fragments = random.sample(range(min_fragments, max_fragments), 1)[0]
        param_num_queries = random.sample(range(min_queries, max_queries), 1)[0]

        problem = add_problem_properties(param_num_fragments, param_num_queries, num_workloads)

        problems.append(problem)
    return problems


def add_problem_properties(param_num_fragments, param_num_queries, workloads):
    param_fragment_size = random.choices(range(1, 3000), k=param_num_fragments)
    param_queries = generate_queries(param_num_queries, param_num_fragments)
    param_query_frequency = [random.choices(range(1, 100), k=param_num_queries)
                             for _ in range(workloads)]
    param_query_cost = random.choices(range(1, 100), k=param_num_queries)
    param_query_ids = [i for i in range(len(param_query_cost))]
    problem = Problem(param_fragment_size, param_queries,
                      param_query_frequency, param_query_cost, param_query_ids,
                      len(param_query_ids))
    return problem


def plot_data(df, min_nodes, max_nodes, problems):
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
    deviation = deviation.drop(columns=['nodes'])
    fig, ax = plt.subplots()
    deviation.plot.bar(ax=ax)
    ax.set(xlabel='Split Strategies', ylabel='%',
           title='%-Deviation from optimum One Split Strategy')
    plt.show()


def plot_heu_vs_opt(df, min_nodes, max_nodes, problems):
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
            if not (name == 'Complete' and y_axis == 'space'):
                group.plot(x='nodes', y=y_axis, label=name, ax=ax)
        plt.xticks([i for i in range(min_nodes, max_nodes + 1)])
        plt.show()
    df = df[df.algo != "Total Replication"]
    deviation = ((df.groupby('algo').mean() / df.groupby('algo').mean().loc['Complete']) - 1) * 100
    deviation = deviation.drop(index=['Complete'])
    deviation = deviation.drop(columns=['nodes'])
    deviation = deviation.drop(columns=['total_replication', 'deviation'])

    fig, ax = plt.subplots()
    deviation.plot.bar(ax=ax)
    ax.set(xlabel='Split Strategies', ylabel='%',
           title='%-Difference from optimum One Split')
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
        fig, axs = plt.subplots(1, 3, figsize=(10, 3))
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
