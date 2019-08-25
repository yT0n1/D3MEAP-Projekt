import os
import sys
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from automated_testing.problem_generation import add_problem_properties
from core_functionality.solver_node import solve_for_tree
from core_functionality.tree_generation import one_split_tree, one_vs_all_split, approximate_tree, prime_factor_tree, \
    dot_export_actual_workload


def runtime_increasing_factors():
    sizes = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
    df = pd.DataFrame(columns=['nodes', 'algo', 'time', 'query', 'fragment', 'space', 'deviation'])
    df.nodes = df.nodes.astype('int')
    df.algo = df.algo.astype('str')
    df.fragment = df.time.astype('int')
    df.space = df.space.astype('int')
    df.query = df.deviation.astype('int')
    for _ in range(3):
        for size in sizes:
            problem = add_problem_properties(size, size, 1)
            s = solve_for_tree(one_split_tree(size), problem, 1200, False, 0)
            df.loc[len(df)] = [size, s.name.split('|')[0], s.time, size, size, s.space,
                               s.deviation]
    df.to_csv('test221.csv', index=False)
    n = df.groupby('nodes', as_index=False).mean()
    q = df.groupby('query', as_index=False).mean()
    f = df.groupby('fragment', as_index=False).mean()
    fig, ax = plt.subplots()
    n.plot(y='time', x='nodes', ax=ax, label='runtime')
    ax.set(xlabel='factor', ylabel='average time in s',
           title='average runtime for factors')
    plt.xticks(sizes)
    plt.show()
    return df


def runtime_increasing_factors_combined():
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
                    s = solve_for_tree(one_split_tree(node), problem, 1200, False, 0)
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
            print(f"\n SOLVING: NODE COUNT {node_count}, PROBLEM {problems.index(problem)} AT {str(datetime.now())}, MAX SIZE {total_replication}")

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
                dot_export_actual_workload(res.tree)

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
                # dot_export_actual_workload(res.tree)

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


def timeout_vs_heuristic_tests(problems, min_node, max_node, should_squeeze, epsilon=0):
    total_results = []
    df = pd.DataFrame(columns=['algo', 'time', 'space', 'deviation', 'nodes'])
    epsilon = 0
    for node in range(min_node, max_node + 1):
        for problem in problems:
            print(
                f"\n SOLVING PROBLEM {problems.index(problem)} WITH {node} NODES AT"
                f" {str(datetime.now())}")
            s5 = solve_for_tree(one_split_tree(node), problem, 900,
                                should_squeeze, epsilon)

            s1 = solve_for_tree(approximate_tree(node, 2), problem, 900,
                                should_squeeze, epsilon)
            s2_time = s1.time
            try:
                s2 = solve_for_tree(one_split_tree(node), problem, s2_time,
                                    should_squeeze, epsilon)
            except:
                print('Run again with first result')

                s2 = solve_for_tree(one_split_tree(node), problem, 900,
                                    should_squeeze, epsilon, True)

            s3 = solve_for_tree(one_vs_all_split(node), problem, 900,
                                should_squeeze, epsilon)
            s4_time = s3.time
            try:
                s4 = solve_for_tree(one_split_tree(node), problem, s4_time,
                                    should_squeeze, epsilon)
            except:
                print('Run again with first result')
                s4 = solve_for_tree(one_split_tree(node), problem, 900,
                                    should_squeeze, epsilon, True)

            s2.name = 'Complete (2-Approx timeout)'
            s4.name = 'Complete (one-vs-all timeout)'
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