from solver_node import solve_for_tree
from tree_generation import one_split_tree, approximate_tree, dot_export_actual_workload, \
    prime_factor_tree, one_vs_all_split, dot_export_ideal_workload


class Problem:
    def __init__(self, param_fragment_size, param_queries, param_query_frequency,
                 param_query_cost, param_query_ids, total_nr_queries):
        self.param_fragment_size = param_fragment_size
        self.param_queries = param_queries
        self.param_query_frequency = param_query_frequency
        self.param_query_cost = param_query_cost
        self.param_query_ids = param_query_ids
        self.total_nr_queries = total_nr_queries


def main():



    dot_export_ideal_workload(prime_factor_tree(6, True, False))
    dot_export_ideal_workload(one_vs_all_split(6))
    dot_export_ideal_workload(approximate_tree(6, 2))
    dot_export_ideal_workload(approximate_tree(6, 4))

if __name__ == '__main__':
    main()

