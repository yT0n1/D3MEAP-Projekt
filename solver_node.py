import copy
from pulp import *
import pulp.solvers

from anytree import Node
from utils import print_location, print_location_adaptive, print_workload, derivation_from_worksplit


def solve_split_adaptive(param_fragment_sizes, param_query_compositions, param_query_frequencies,
                         param_query_costs,
                         param_num_nodes, param_query_ids, name, workshare_split, timeout_sec,
                         epsilon_factor,
                         should_squeeze=True, use_normed=False):
    assert round(sum(workshare_split), 10) == 1
    assert len(workshare_split) == param_num_nodes

    def objective():
        sum = 0
        for f in range(param_num_fragments):
            for n in range(param_num_nodes):
                sum += var_location[(f, n)] * param_fragment_sizes[f]
        sum += epsilon_factor * var_epsilon
        return sum

    def non_squeeze_objective():
        sum = 0
        for f in range(param_num_fragments):
            for n in range(param_num_nodes):
                sum += var_location[(f, n)] * param_fragment_sizes[f]
        return sum

    def normed_objective():
        value = 0
        for f in range(param_num_fragments):
            for n in range(param_num_nodes):
                value += (var_location[(f, n)] * param_fragment_sizes[f])/sum(param_fragment_sizes)
        value += epsilon_factor * var_epsilon
        return value

    def nb_1(problem_instance):
        for q in param_query_ids:
            c = sum([var_runnable[(q, n)] for n in range(param_num_nodes)]) >= 1
            problem_instance += c
        return problem_instance

    def nb_2(problem_instance):
        for q in param_query_ids:
            c = sum([var_workshare[(q, n)] for n in range(param_num_nodes)]) == 1
            problem_instance += c
        return problem_instance

    def nb_3(problem_instance):
        for n in range(param_num_nodes):
            for q in param_query_ids:
                c = var_runnable[(q, n)] * sum(param_query_compositions[q]) <= sum(
                    [var_location[(f, n)] * param_query_compositions[q][f] for f in
                     range(param_num_fragments)])
                problem_instance += c
        return problem_instance

    def nb_4(problem_instance):
        for n in range(param_num_nodes):
            for q in param_query_ids:
                c = var_workshare[(q, n)] <= var_runnable[(q, n)]
                problem_instance += c
        return problem_instance

    def nb_5(problem_instance):
        for n in range(param_num_nodes):
            for w in range(len(param_query_workload)):
                c = (sum([var_workshare[(q, n)] * param_query_workload[w][q] for q in
                          param_query_ids]) / param_total_workload[w])  <= var_epsilon
                problem_instance += c
        return problem_instance

    def nb_5_no_squeeze(problem_instance):
        for n in range(param_num_nodes):
            for w, qw in enumerate(param_query_workload):
                c = (sum([var_workshare[(q, n)] * qw[q] for q in
                          param_query_ids]) / param_total_workload[w]) == workshare_split[n]
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
    var_epsilon = LpVariable(name="epsilon", lowBound=0, upBound=1, cat='Continuous')

    if should_squeeze:
        problem += objective()
        problem = nb_5(problem)
    elif use_normed:
        problem += normed_objective()
        problem = nb_5(problem)
    else:
        problem += non_squeeze_objective()
        problem = nb_5_no_squeeze(problem)
    problem = nb_1(problem)
    problem = nb_2(problem)
    problem = nb_3(problem)
    problem = nb_4(problem)


    solver = pulp.solvers.GUROBI_CMD(options=[('TimeLimit', timeout_sec)])
    solver.actualSolve(problem)

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
    print("##### WORKLOAD PERCENTAGES #####")
    workload_percentages = print_workload(var_workshare, param_num_nodes, param_query_workload, param_query_ids)

    print("")

    sum_workload = 0
    for loc in var_workshare.keys():
        sum_workload += var_workshare[loc].varValue

    print("Sum Workload: ", str(sum_workload))
    if should_squeeze:
        print("Epsilon:", str(var_epsilon.value()), "(Optimum ",
              "{})".format(str(float(1) / param_num_nodes)))
        space_required = problem.objective.value() - epsilon_factor * var_epsilon.value()
    elif use_normed:
        print("Epsilon:", str(var_epsilon.value()), "(Optimum ",
              "{})".format(str(float(1) / param_num_nodes)))
        space_required = (problem.objective.value() - epsilon_factor * var_epsilon.value()) * sum(param_fragment_sizes)
    else:
        space_required = problem.objective.value()
    print("Objective Value:", str(space_required))

    print('Deviation ', derivation_from_worksplit(workload_percentages, workshare_split))
    print('Nr. Vars:', problem.numVariables())
    print('Solved:', name, '\n\n\n')
    return problem, var_location, var_runnable, var_workshare, space_required, workload_percentages


class SolverNode(Node):
    def __init__(self, name, should_squeeze=True, use_normed=False, **kwargs):
        super().__init__(name, **kwargs)
        self.problem = None
        self.split_ratio = None
        self.workshare_split = None
        self.should_squeeze = should_squeeze
        self.use_normed = use_normed
        self.workshare_deviation = 0
        self.epsilon_factor = 10_000

    def solve(self, timeout_secs=60):
        if self.is_leaf:
            mask = [0] * len(self.problem.param_fragment_size)
            for q in self.problem.param_query_ids:
                mask = [a | b for a, b in zip(mask, self.problem.param_queries[q])]
            size = sum(self.problem.param_fragment_size[f] * mask[f] for f in range(len(mask)))
            return size
        elif not self.problem.param_query_ids:
            print("Node Skipped: ",self.name)
            for c in self.children:
                p = copy.deepcopy(self.problem)
                self.workshare_split = []
                c.problem = p
            return 0
        solution, var_location, var_runnable, var_workshare, space, workload_percentages = \
            solve_split_adaptive(
            self.problem.param_fragment_size, self.problem.param_queries,
            self.problem.param_query_frequency,
            self.problem.param_query_cost, len(self.children), self.problem.param_query_ids,
            self.name, self.split_ratio, timeout_secs, self.root.epsilon_factor,
            self.root.should_squeeze,
            self.root.use_normed)

        self.workshare_split = workload_percentages
        self.workshare_deviation = derivation_from_worksplit(self.workshare_split, self.split_ratio)
        for c in range(len(self.children)):
            queries_on_child = [q for q in self.problem.param_query_ids
                                if var_runnable[(q, c)].value() and var_workshare[(q, c)].value()]
            # we adapt the cost of a query by the share of work that is done on the child
            # for this we do a dictionary only with the indeces from the queries we need
            query_cost_on_child = [var_workshare[(q, c)].value() * self.problem.param_query_cost[
                q] if q in queries_on_child else 0 for q in range(self.problem.total_nr_queries)]
            p = copy.deepcopy(self.problem)
            p.param_query_ids = queries_on_child
            p.param_query_cost = query_cost_on_child
            self.children[c].problem = p
        return 0

    def set_split_ratio(self):
        reachable_leaves = len(self.leaves)
        self.split_ratio = [len(c.leaves) / reachable_leaves for c in self.children]
