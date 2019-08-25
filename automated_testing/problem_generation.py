import random
import numpy as np

"""
    Problem Generation:
    This file includes all methods used for generating problems
"""


class Problem:
    def __init__(self, param_fragment_size, param_queries, param_query_frequency,
                 param_query_cost, param_query_ids, total_nr_queries):
        self.param_fragment_size = param_fragment_size
        self.param_queries = param_queries
        self.param_query_frequency = param_query_frequency
        self.param_query_cost = param_query_cost
        self.param_query_ids = param_query_ids
        self.total_nr_queries = total_nr_queries

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
