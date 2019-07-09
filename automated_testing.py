import copy
import random
from statistics import median

import matplotlib.pyplot as plt

from playground import solve_for_tree, Problem
from tree_generation import one_split_tree, one_vs_all_split, approximate_tree, prime_factor_tree, \
    dot_export_actual_workload


def generate_queries(num_queries, num_fragments):
    queries = []
    for i in range(num_queries):
        temp_list = []
        for j in range(num_fragments):
            temp_list.append(random.choice([0, 1]))
        queries.append(temp_list)
    return queries

def automated_test():
    total_results = []

    # Configuration
    min_nodes = 4
    max_nodes = 12
    timeout = 3
    num_epochs = 3

    problems = []
    for epoch in range(num_epochs):
        param_num_fragments = random.sample(range(3, 10), 1)[0]
        param_num_queries = random.sample(range(5, 10), 1)[0]

        param_fragment_size = random.sample(range(1, 100), param_num_fragments)
        param_queries = generate_queries(param_num_queries, param_num_fragments)
        param_query_frequency = [random.sample(range(1, 100), param_num_queries) for i in range(3)]
        param_query_cost = random.sample(range(1, 100), param_num_queries)
        param_query_ids = [i for i in range(len(param_query_cost))]

        problems.append(Problem(param_fragment_size, param_queries,
                          param_query_frequency, param_query_cost, param_query_ids,
                          len(param_query_ids)))

    for node_count in range(min_nodes, max_nodes+1):
        epoch_results = []
        for proto_problem in problems:
            problem = copy.deepcopy(proto_problem)

            s1 = solve_for_tree(prime_factor_tree(node_count, False, False), problem, timeout)
            s2 = solve_for_tree(prime_factor_tree(node_count, False, True), problem, timeout)
            s3 = solve_for_tree(prime_factor_tree(node_count, True, False), problem, timeout)
            s4 = solve_for_tree(prime_factor_tree(node_count, True, True), problem, timeout)

            s5 = solve_for_tree(one_split_tree(node_count), problem, timeout)

            s6 = solve_for_tree(one_vs_all_split(node_count), problem, timeout)
            dot_export_actual_workload(s6.tree, str(node_count))

            s7 = solve_for_tree(approximate_tree(node_count, 2), problem, timeout)
            s8 = solve_for_tree(approximate_tree(node_count, 3), problem, timeout)
            s9 = solve_for_tree(approximate_tree(node_count, 4), problem, timeout)
            s10 = solve_for_tree(approximate_tree(node_count, 5), problem, timeout)
            s11 = solve_for_tree(approximate_tree(node_count, 6), problem, timeout)

            epoch_results.append([s1,s2,s3,s4,s5,s6,s7,s8,s9,s10,s11])
        total_results.append(epoch_results)

    legend_labels = [strategy.name for strategy in total_results[0][0]]
    space_per_strategy = []
    space_per_strategy_avg = []
    deviation_per_strategy = []
    time_per_strategy = []

    # Get the results which you want
    for node_level in total_results:
        space_per_strategy.append([median([node_level[i][j].space for i in range(len(node_level))]) for j in range(len(node_level[0]))])
        deviation_per_strategy.append([median([node_level[i][j].deviation for i in range(len(node_level))]) for j in range(len(node_level[0]))])
        time_per_strategy.append([median([node_level[i][j].time for i in range(len(node_level))]) for j in range(len(node_level[0]))])

    # Reformat Lists
    space_plot_data = []
    deviation_plot_data = []
    time_plot_data = []
    for j in range(len(legend_labels)):
        space_plot_data.append([space_per_strategy[i][j] for i in range(len(space_per_strategy))])
        deviation_plot_data.append([deviation_per_strategy[i][j] for i in range(len(deviation_per_strategy))])
        time_plot_data.append([time_per_strategy[i][j] for i in range(len(time_per_strategy))])

    node_labels = [i for i in range(min_nodes, max_nodes+1)]

    # Plot Space Graph
    fig, ax = plt.subplots()
    for line in space_plot_data:
        ax.plot(node_labels, line)
    ax.set(xlabel='Node Count', ylabel='Space', title='Average Space per Node Count')
    ax.legend(legend_labels)
    plt.xticks(node_labels)
    plt.show()

    # Plot Deviation Graph
    fig, ax = plt.subplots()
    for line in deviation_plot_data:
        ax.plot(node_labels, line)
    ax.set(xlabel='Node Count', ylabel='Deviation', title='Average Deviation per Node Count')
    ax.legend(legend_labels)
    plt.xticks(node_labels)
    plt.show()

    # Plot Deviation Graph
    fig, ax = plt.subplots()
    for line in time_plot_data:
        ax.plot(node_labels, line)
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



if __name__ == '__main__':
    automated_test()
