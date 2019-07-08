import random

from main import solve_for_tree, Problem
from tree_generation import one_split_tree, one_vs_all_split


def generate_queries(num_queries, num_fragments):
    queries = []
    for i in range(num_queries):
        temp_list = []
        for j in range(num_fragments):
            temp_list.append(random.choice([0, 1]))
        queries.append(temp_list)
    return queries

def automated_test(num_epochs):
    total_results = []
    for node_count in range(2,5):
        epoch_results = []
        for epoch in range(num_epochs):
            param_num_fragments = 7
            param_num_queries = 7

            param_fragment_size = random.sample(range(1, 100), param_num_fragments)
            param_queries = generate_queries(param_num_queries, param_num_fragments)
            param_query_frequency = [random.sample(range(1, 100), param_num_queries) for i in range(3)]
            param_query_cost = random.sample(range(1, 100), param_num_queries)
            param_query_ids = [0, 1, 2, 3, 4, 5, 6]

            problem = Problem(param_fragment_size, param_queries,
                              param_query_frequency, param_query_cost, param_query_ids,
                              len(param_query_ids))

            #s1 = solve_for_tree(prime_factor_tree(node_count, True, True), problem)
            s2 = solve_for_tree(one_split_tree(node_count), problem, 2)
            s3 = solve_for_tree(one_vs_all_split(node_count), problem, 2)

            epoch_results.append([])
            #epoch_results[epoch].append(s1)
            epoch_results[epoch].append(s2)
            epoch_results[epoch].append(s3)
        total_results.append(epoch_results)

    for node_level in total_results:
        sum_s1 = sum([node_level[i][0].space for i in range(len(node_level))]) / num_epochs
        sum_s2 = sum([node_level[i][1].space for i in range(len(node_level))]) / num_epochs
        print(sum_s1, sum_s2)