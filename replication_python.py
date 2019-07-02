from anytree import RenderTree, DoubleStyle, LevelOrderIter

from solver_node import solve_split_adaptive
from tree_generation import prime_factor_tree, binary_tree


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
    param_num_nodes = 10

    param_fragment_size = [1, 2, 3, 4, 4, 1, 2]
    param_queries = [[1, 1, 0, 1, 1, 1, 0],
                     [0, 0, 0, 0, 1, 0, 0],
                     [0, 1, 1, 0, 1, 1, 0],
                     [0, 0, 1, 1, 1, 1, 0],
                     [0, 1, 1, 0, 0, 0, 1],
                     [1, 1, 0, 0, 0, 1, 0],
                     [1, 0, 1, 0, 0, 0, 1],
                     [0, 1, 1, 0, 0, 1, 1],
                     [1, 0, 0, 0, 1, 1, 0]]
    param_query_frequency = [[4, 5, 6, 1, 2, 3, 4, 5, 12],
                             [1, 5, 6, 6, 3, 3, 3, 1, 14],
                             [5, 1, 2, 1, 6, 3, 1, 9, 9]]
    param_query_ids = [0, 1, 2, 3, 4, 5, 6, 7, 8]
    param_query_cost = [10, 20, 25, 15, 22, 33, 21, 11, 23]

    assert len(param_query_frequency[0]) == len(param_query_cost) \
           == len(param_query_ids) == len(param_queries)

    problem = Problem(param_fragment_size, param_queries,
                      param_query_frequency, param_query_cost, param_query_ids,
                      len(param_query_ids))

    s1 = solve_for_tree(prime_factor_tree(param_num_nodes), problem)
    s2 = solve_for_tree(prime_factor_tree(param_num_nodes, True), problem)
    s3 = solve_for_tree(binary_tree(param_num_nodes), problem)

    # The leave nodes present no problem and are not solved, thus the tree that is defined here
    # has only three splits !!!!!

    #
    problem = solve_split_adaptive(param_fragment_size, param_queries, param_query_frequency,
                                   param_query_cost, param_num_nodes, param_query_ids, 'complete',
                                   60)

    print(s1, s2, s3, problem[4])

    print('Minimum possible would be:', sum(param_fragment_size))
    print('Workload per query: ',
          [[a * b for a, b in zip(param_query_frequency[i], param_query_cost)] for
           i in range(len(param_query_frequency))])


def solve_for_tree(tree_root, problem):
    print('\nSolving Tree', tree_root.name)
    print(RenderTree(tree_root, style=DoubleStyle))
    tree_root.problem = problem
    total_space = [node.solve() for node in LevelOrderIter(tree_root)]
    print('Split Space required', total_space)
    print('In total ', sum(total_space))
    return sum(total_space)


if __name__ == '__main__':
    main()

# mingap und timelim
