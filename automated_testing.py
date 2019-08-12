import random
from statistics import median, mean
import matplotlib.pyplot as plt
import pandas as pd

from playground import solve_for_tree, Problem
from tree_generation import one_split_tree, one_vs_all_split, approximate_tree, prime_factor_tree, \
    dot_export_actual_workload
import matplotlib as mpl

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
    min_nodes = 4
    max_nodes = 6
    timeout = 15
    num_problems = 5

    problems = generate_problems(num_problems)

    total_results, df = test_with_nodes(min_nodes, max_nodes, problems, timeout)
    y_axises = ['time', 'space', 'deviation']
    for y_axis in y_axises:
        fig, ax = plt.subplots()
        ax.set(xlabel='Node Count', ylabel=y_axis, title=f'Average {y_axis} per node count')
        plot_group = df.groupby(['algo', 'nodes'], as_index=False)[y_axis].mean().groupby('algo')
        for name, group in plot_group:
            group.plot(x='nodes', y=y_axis, label=name, ax=ax)
        plt.xticks([i for i in range(min_nodes, max_nodes + 1)])
        plt.show()
    # exit()
    legend_labels = [strategy.name for strategy in total_results[0][0]]
    space_per_strategy = []
    space_per_strategy_avg = []
    deviation_per_strategy = []
    time_per_strategy = []

    # Get the results which you want
    for node_level in total_results:
        space_per_strategy.append(
            [mean([node_level[i][j].space for i in range(len(node_level))]) for j in
             range(len(node_level[0]))])
        deviation_per_strategy.append(
            [mean([node_level[i][j].deviation for i in range(len(node_level))]) for j in
             range(len(node_level[0]))])
        time_per_strategy.append(
            [mean([node_level[i][j].time for i in range(len(node_level))]) for j in
             range(len(node_level[0]))])

    # Reformat Lists
    space_plot_data = []
    deviation_plot_data = []
    time_plot_data = []
    for j in range(len(legend_labels)):
        space_plot_data.append([space_per_strategy[i][j] for i in range(len(space_per_strategy))])
        deviation_plot_data.append(
            [deviation_per_strategy[i][j] for i in range(len(deviation_per_strategy))])
        time_plot_data.append([time_per_strategy[i][j] for i in range(len(time_per_strategy))])
    node_labels = [i for i in range(min_nodes, max_nodes + 1)]

    # Plot Space Graph
    fig, ax = plt.subplots()
    for line in space_plot_data:
        ax.plot(node_labels, line, alpha=0.5)
    ax.set(xlabel='Node Count', ylabel='Space', title='Average Space per Node Count')
    ax.legend(legend_labels)
    plt.xticks(node_labels)
    plt.show()

    # Plot Deviation Graph
    fig, ax = plt.subplots()
    for line in deviation_plot_data:
        ax.plot(node_labels, line, alpha=0.5)
    ax.set(xlabel='Node Count', ylabel='Deviation', title='Average Deviation per Node Count')
    ax.legend(legend_labels)
    plt.xticks(node_labels)
    plt.show()

    # Plot Deviation Graph
    fig, ax = plt.subplots()
    for line in time_plot_data:
        ax.plot(node_labels, line, alpha=0.5)
    ax.set(xlabel='Node Count', ylabel='Runtime in Seconds', title='Average Runtime per Node Count')
    ax.legend(legend_labels)
    plt.xticks(node_labels)
    plt.show()

    # Print Space & Deviation
    for i, label in enumerate(legend_labels):
        print("Space for Tree: ", label)
        print(space_plot_data[i])
        print("Deviation for Tree: ", label)
        print(deviation_plot_data[i])
        print("")

    # Deviation from One Split
    one_split_space = space_plot_data[legend_labels.index("One Split")]
    deviations = []
    for strategy_results in space_plot_data:
        deviations.append(
            [strategy_results[node_level] - one_split_space[node_level] for node_level in
             range(len(strategy_results))])
    fig, ax = plt.subplots()
    for line in deviations:
        ax.plot(node_labels, line, alpha=0.5)
    ax.set(xlabel='Node Count', ylabel='Deviation', title='Average Space Deviation from OneSplit')
    ax.legend(legend_labels)
    plt.xticks(node_labels)
    plt.show()


def test_with_nodes(min_nodes, max_nodes, problems, timeout):
    total_results = []
    df = pd.DataFrame(columns=['nodes', 'algo', 'time', 'space', 'deviation'])

    for node_count in range(min_nodes, max_nodes + 1):
        epoch_results = []
        for problem in problems:
            # s1 = solve_for_tree(one_split_tree(node_count), problem, timeout)
            s11 = solve_for_tree(one_split_tree(node_count), problem, timeout)

            s2 = solve_for_tree(prime_factor_tree(node_count, False, False), problem, timeout)
            s3 = solve_for_tree(prime_factor_tree(node_count, True, False), problem, timeout)

            s4 = solve_for_tree(one_vs_all_split(node_count), problem, timeout)

            s5 = solve_for_tree(approximate_tree(node_count, 2), problem, timeout)
            s6 = solve_for_tree(approximate_tree(node_count, 3), problem, timeout)
            s7 = solve_for_tree(approximate_tree(node_count, 4), problem, timeout)
            s8 = solve_for_tree(approximate_tree(node_count, 5), problem, timeout)
            s9 = solve_for_tree(approximate_tree(node_count, 6), problem, timeout)
            s10 = solve_for_tree(approximate_tree(node_count, 7), problem, timeout)

            xx_results = [s2, s3, s4, s5, s6, s7, s8, s9, s10, s11]
            for res in xx_results:
                # The name is split due to the very verbose and varying naming for prime trees
                df.loc[len(df)] = [node_count, res.name.split('|')[0], res.time, res.space,
                                   res.deviation]
            # for xx_r in xx_results:
            # dot_export_actual_workload(xx_r.tree)
            epoch_results.append(xx_results)
        total_results.append(epoch_results)
    df.nodes = df.nodes.astype('int')
    df.algo = df.algo.astype('str')
    df.time = df.time.astype('float')
    df.space = df.space.astype('int')
    df.deviation = df.deviation.astype('float')
    return total_results, df


def generate_problems(num_epochs):
    problems = []
    for epoch in range(num_epochs):
        param_num_fragments = random.sample(range(10, 20), 1)[0]
        param_num_queries = random.sample(range(6, 10), 1)[0]

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


if __name__ == '__main__':
    automated_test()
