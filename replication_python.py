import copy

from pulp import *
from anytree import PreOrderIter, RenderTree, DoubleStyle
import itertools
from anytree import Node as AbstractNode

from utils import print_location, print_location_adaptive


def solve_split_adaptive(param_fragment_sizes, param_query_compositions, param_query_frequencies,
                         param_query_costs,
                         param_num_nodes, param_query_ids, name):
    epsilon_factor = 1000

    def objective():
        sum = 0
        for f in range(param_num_fragments):
            for n in range(param_num_nodes):
                sum += var_location[(f, n)] * param_fragment_sizes[f]
        sum += epsilon_factor * var_epsilon
        return sum

    def nb_1(problem_instance):
        for q in param_query_ids:
            c = sum([var_runnable[(q, n)] for n in range(param_num_nodes)]) >= 1
            problem_instance += c
        return problem_instance

    def nb_2(problem_instance):
        for q in param_query_ids:
            c = sum([var_workshare[(q, n)] for n in range(param_num_nodes)]) >= 1
            problem_instance += c
        return problem_instance

    def nb_3(problem_instance):
        for n in range(param_num_nodes):
            for q in param_query_ids:
                c = var_runnable[(q, n)] * sum(
                    [param_query_compositions[q][f] for f in range(param_num_fragments)]) <= sum(
                    [var_location[(f, n)] * param_query_compositions[q][f] for f in
                     range(param_num_fragments)])
                problem_instance += c
        return problem_instance

    def nb_4(problem_instance):
        for n in range(param_num_nodes):
            for q in param_query_ids:
                c = var_workshare[(q, n)] <= var_runnable[q, n]
                problem_instance += c
        return problem_instance

    def nb_5(problem_instance):
        for n in range(param_num_nodes):
            for w in range(len(param_query_workload)):
                c = (sum([var_workshare[(q, n)] * param_query_workload[w][q] for q in
                          param_query_ids]) / param_total_workload[w]) <= var_epsilon
                problem_instance += c
        return problem_instance

    problem = LpProblem("replication", LpMinimize)

    param_num_fragments = len(param_fragment_sizes)

    param_query_workload = [[a * b for a, b in zip(param_query_frequencies[i], param_query_costs)]
                            for
                            i in range(len(param_query_frequencies))]
    param_total_workload = [sum(param_query_workload[i]) for i in range(len(param_query_workload))]

    location_dict_index = itertools.product(range(param_num_fragments), range(param_num_nodes))
    runnable_dict_index = itertools.product(param_query_ids, range(param_num_nodes))
    workshare_dict_index = itertools.product(param_query_ids, range(param_num_nodes))

    var_location = LpVariable.dicts(name="location", indexs=location_dict_index, lowBound=0,
                                    upBound=1, cat='Integer')
    var_runnable = LpVariable.dicts(name="runnable", indexs=runnable_dict_index, lowBound=0,
                                    upBound=1, cat='Integer')
    var_workshare = LpVariable.dicts(name="workshare", indexs=workshare_dict_index, lowBound=0,
                                     cat='Continuous')
    var_epsilon = LpVariable(name="epsilon", lowBound=0, cat='Continuous')

    problem += objective()
    problem = nb_1(problem)
    problem = nb_2(problem)
    problem = nb_3(problem)
    problem = nb_4(problem)
    problem = nb_5(problem)

    problem.solve()
    print('\n\nSOLVING:', name)
    print("")
    print("##### LOCATION #####")
    print_location(var_location, param_num_nodes, param_num_fragments)

    print("")
    print("##### RUNNABLE #####")
    print_location_adaptive(var_runnable, param_num_nodes, param_query_ids)

    print("")
    print("##### WORKSHARE #####")
    print_location_adaptive(var_workshare, param_num_nodes, param_query_ids, False)

    print("")

    sum_workload = 0
    for loc in var_workshare.keys():
        sum_workload += var_workshare[loc].varValue

    print("Sum Workload: ", str(sum_workload))
    print("Objective Value:", str(problem.objective.value() - epsilon_factor * var_epsilon.value()))
    print("Epsilon:", str(var_epsilon.value()), "(Optimum ",
          "{})".format(str(float(1) / param_num_nodes)))
    print('Nr. Vars:', problem.numVariables())
    print('Solved:', name, '\n\n\n')
    space_required = problem.objective.value() - epsilon_factor * var_epsilon.value()
    return problem, var_location, var_runnable, var_workshare, space_required


class Problem:
    def __init__(self, param_fragment_size, param_queries, param_query_frequency,
                 param_query_cost, param_query_ids, total_nr_queries):
        self.param_fragment_size = param_fragment_size
        self.param_queries = param_queries
        self.param_query_frequency = param_query_frequency
        self.param_query_cost = param_query_cost
        self.param_query_ids = param_query_ids
        self.total_nr_queries = total_nr_queries

class Node(AbstractNode):

    def solve(self):
        if not self.children:
            size = 0
            for q in self.problem.param_query_ids:
                fragments = self.problem.param_queries[q]
                size += sum(self.problem.param_fragment_size[f] * fragments[f] for f in range(
                    len(fragments)))
            return size

        # we use the dynamicness of pyhton to set an attribute here which will be accessed later.
        # Not nice, but, oh well...
        solution, var_location, var_runnable, var_workshare, space = solve_split_adaptive(
            self.problem.param_fragment_size, self.problem.param_queries,
            self.problem.param_query_frequency,
            self.problem.param_query_cost, len(self.children), self.problem.param_query_ids,
            self.name)
        for c in range(len(self.children)):
            queries_on_child = [q for q in self.problem.param_query_ids
                                if var_runnable[(q, c)].value()]
            # we adapt the cost of a query by the share of work that is done on the child
            # for this we do a dictionary only with the indeces from the queries we need
            query_cost_on_child = [var_workshare[(q, c)].value() * self.problem.param_query_cost[
                q] if q in queries_on_child else 0 for q in range(self.problem.total_nr_queries)]
            p = copy.deepcopy(self.problem)
            p.param_query_ids = queries_on_child
            p.param_query_cost = query_cost_on_child
            self.children[c].problem = p
        return 0


def main():
    param_num_nodes = 4


    param_fragment_size = [1, 2, 3, 4, 4, 1, 2]
    param_queries = [[1, 1, 0, 1, 1, 1, 0],
                     [0, 0, 0, 0, 1, 0, 0],
                     [0, 1, 1, 0, 1, 1, 0],
                     [0, 0, 1, 1, 1, 1, 0],
                     [0, 1, 1, 0, 0, 0, 1],
                     [1, 1, 0, 0, 0, 1, 0],
                     [1, 0, 1, 0, 0, 0, 1],
                     [0, 1, 1, 0, 0, 1, 1]]
    param_query_frequency = [[4, 5, 6, 1, 2, 3, 4, 5],
                             [1, 5, 6, 6, 3, 3, 3, 1],
                             [5, 1, 2, 1, 6, 3, 1, 9]]
    param_query_ids = [0, 1, 2, 3, 4, 5, 6, 7]
    param_query_cost = [10, 20, 25, 15, 22, 33, 21, 11]

    assert len(param_query_frequency[0]) == len(param_query_cost) \
           == len(param_query_ids) == len(param_queries)

    split1 = tree1()
    print(RenderTree(split1, style=DoubleStyle))
    split1.problem = Problem(param_fragment_size, param_queries,
                             param_query_frequency, param_query_cost, param_query_ids,
                             len(param_query_ids))

    #total_space = [node.solve() for node in PreOrderIter(split1)]
    #print('Split Space required', total_space)


    root2 = tree2()
    print(RenderTree(root2, style=DoubleStyle))
    root2.problem = Problem(param_fragment_size, param_queries,
                             param_query_frequency, param_query_cost, param_query_ids,
                             len(param_query_ids))


    total_space = [node.solve() for node in PreOrderIter(root2)]
    print('Split Space required', total_space)
    # The leave nodes present no problem and are not solved, thus the tree that is defined here
    # has only three splits !!!!!

    #
    problem = solve_split_adaptive(param_fragment_size, param_queries, param_query_frequency,
                          param_query_cost, param_num_nodes,param_query_ids, 'complete')

    print('Minimum possible would be:', sum(param_fragment_size))
    print('Workload per queriy: ', [[a * b for a, b in zip(param_query_frequency[i], param_query_cost)] for
                            i in range(len(param_query_frequency))])

def tree1():
    "Binary"
    split1 = Node("split1")
    split2 = Node("split2", parent=split1)
    split3 = Node("split3", parent=split1)
    split4 = Node("split4", parent=split2)
    split5 = Node("split5", parent=split2)
    split6 = Node("split6", parent=split3)
    split7 = Node("split7", parent=split3)
    Node("l1", parent=split4)
    Node("l2", parent=split4)
    Node("l3", parent=split5)
    Node("l4", parent=split5)
    Node("l5", parent=split6)
    Node("l6", parent=split6)
    Node("l7", parent=split7)
    Node("l8", parent=split7)

    return split1


def tree2():
    "four split"
    root = Node("split1")
    split2 = Node("split2", parent=root)
    split3 = Node("split3", parent=root)
    split4 = Node("split4", parent=root)
    split5 = Node("split5", parent=root)
    Node("l5", parent=split2)
    Node("l6", parent=split2)
    Node("l7", parent=split3)
    Node("l8", parent=split3)
    Node("l1", parent=split4)
    Node("l2", parent=split4)
    Node("l3", parent=split5)
    Node("l4", parent=split5)

    return root



if __name__ == '__main__':
    main()
