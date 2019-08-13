import random

import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd

from playground import Problem
from solver_node import solve_for_tree
from tree_generation import one_split_tree, one_vs_all_split, approximate_tree, prime_factor_tree

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
    max_nodes = 12
    timeout = 15
    num_problems = 3
    should_squeeze = False
    epsilon_factor = 10000

    problems = generate_problems(num_problems)

    total_results, df = test_with_nodes(min_nodes, max_nodes, problems, timeout, should_squeeze, epsilon_factor)
    plot_data(df, min_nodes, max_nodes)
    df.to_csv("out.csv")


def test_with_nodes(min_nodes, max_nodes, problems, timeout, should_squeeze, epsilon_factor):
    total_results = []
    df = pd.DataFrame(columns=['nodes', 'algo', 'time', 'space', 'deviation'])

    for node_count in range(min_nodes, max_nodes + 1):
        epoch_results = []
        for problem in problems:
            # s1 = solve_for_tree(one_split_tree(node_count), problem, timeout)
            s11 = solve_for_tree(one_split_tree(node_count), problem, timeout, should_squeeze, epsilon_factor)

            s2 = solve_for_tree(prime_factor_tree(node_count, False, False), problem, timeout, should_squeeze, epsilon_factor)
            s3 = solve_for_tree(prime_factor_tree(node_count, True, False), problem, timeout, should_squeeze, epsilon_factor)

            s4 = solve_for_tree(one_vs_all_split(node_count), problem, timeout, should_squeeze, epsilon_factor)

            s5 = solve_for_tree(approximate_tree(node_count, 2), problem, timeout, should_squeeze, epsilon_factor)
            s6 = solve_for_tree(approximate_tree(node_count, 3), problem, timeout, should_squeeze, epsilon_factor)
            s7 = solve_for_tree(approximate_tree(node_count, 4), problem, timeout, should_squeeze, epsilon_factor)
            s8 = solve_for_tree(approximate_tree(node_count, 5), problem, timeout, should_squeeze, epsilon_factor)
            s9 = solve_for_tree(approximate_tree(node_count, 6), problem, timeout, should_squeeze, epsilon_factor)
            s10 = solve_for_tree(approximate_tree(node_count, 7), problem, timeout, should_squeeze, epsilon_factor)

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


def generate_problems(num_epochs):
    problems = []
    for epoch in range(num_epochs):
        param_num_fragments = random.sample(range(20, 30), 1)[0]
        param_num_queries = random.sample(range(10, 15), 1)[0]

        param_fragment_size = random.choices(range(1, 100), k=param_num_fragments)
        param_queries = generate_queries(param_num_queries, param_num_fragments)
        param_query_frequency = [random.choices(range(1, 100), k=param_num_queries) for i in
                                 range(1)]
        param_query_cost = random.choices(range(1, 100), k=param_num_queries)
        param_query_ids = [i for i in range(len(param_query_cost))]

        problems.append(Problem(param_fragment_size, param_queries,
                                param_query_frequency, param_query_cost, param_query_ids,
                                len(param_query_ids)))
    return problems


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

    deviation = ((df.groupby('algo').mean() / df.groupby('algo').mean().loc['Complete']) - 1)*100
    deviation = deviation.drop(columns=['nodes'])
    fig, ax = plt.subplots()
    ax.set(xlabel='Split Strategies', ylabel='%',
           title='%-Deviation from optimum One Split Strategy')
    deviation.plot.bar(ax=ax)
    plt.show()


if __name__ == '__main__':
    automated_test()
