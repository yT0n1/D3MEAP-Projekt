from pulp import *
import random


def generate_queries(param_num_queries, param_num_fragments):
    queries = []
    for i in range(param_num_queries):
        temp_list = []
        for j in range(param_num_fragments):
            temp_list.append(random.choice([0, 1]))
        queries.append(temp_list)
    return queries


def solve_split(param_fragment_size, param_queries, param_query_frequency, param_query_cost, param_num_nodes):

    def generate_index_dict(first_index, second_index):
        dict_index = []
        for i in range(first_index):
            for j in range(second_index):
                dict_index.append((i, j))
        return dict_index

    def objective():
        sum = 0
        for f in range(param_num_fragments):
            for n in range(param_num_nodes):
                sum += var_location[(f,n)] * param_fragment_size[f]
        return sum

    def nb_1(problem_instance):
        for q in range(param_num_queries):
            c = sum([var_runnable[(q,n)] for n in range(param_num_nodes)]) >= 1
            problem_instance += c
        return problem_instance

    def nb_2(problem_instance):
        for q in range(param_num_queries):
            c = sum([var_workshare[(q,n)] for n in range(param_num_nodes)]) >= 1
            problem_instance += c
        return problem_instance

    def nb_3(problem_instance):
        for n in range(param_num_nodes):
            for q in range(param_num_queries):
                c = var_runnable[(q,n)] * sum([param_queries[q][f] for f in range(param_num_fragments)]) <= sum([var_location[(f,n)] * param_queries[q][f] for f in range(param_num_fragments)])
                problem_instance += c
        return problem_instance

    def nb_4(problem_instance):
        for n in range(param_num_nodes):
            for q in range(param_num_queries):
                c = var_workshare[(q,n)] <= var_runnable[q,n]
                problem_instance += c
        return problem_instance

    def nb_5(problem_instance):
        for n in range(param_num_nodes):
            c = (sum([var_workshare[(q,n)] * param_query_workload[q] for q in range(param_num_queries)]) / param_total_workload) == (1 / param_num_nodes)
            problem_instance += c
        return problem_instance

    problem = LpProblem("replication", LpMinimize)

    param_num_fragments = len(param_fragment_size)
    param_num_queries = len(param_query_cost)

    param_query_workload = [a*b for a,b in zip(param_query_frequency, param_query_cost)]
    param_total_workload = sum(param_query_workload)

    location_dict_index = generate_index_dict(param_num_fragments, param_num_nodes)
    runnable_dict_index = generate_index_dict(param_num_queries, param_num_nodes)
    workshare_dict_index = generate_index_dict(param_num_queries, param_num_nodes)

    var_location = LpVariable.dicts(name="location", indexs=location_dict_index, lowBound=0, upBound=1, cat='Integer')
    var_runnable = LpVariable.dicts(name="runnable", indexs=runnable_dict_index, lowBound=0, upBound=1, cat='Integer')
    var_workshare = LpVariable.dicts(name="workshare", indexs=workshare_dict_index, lowBound=0, cat='Continuous')

    problem += objective()
    problem = nb_1(problem)
    problem = nb_2(problem)
    problem = nb_3(problem)
    problem = nb_4(problem)
    problem = nb_5(problem)

    print(problem)
    problem.solve()

    print("")
    print("##### LOCATION #####")
    for loc in var_location.keys():
        print(str(loc) + " " + str(var_location[loc].varValue))

    print("")
    print("##### RUNNABLE #####")
    for loc in var_runnable.keys():
        print(str(loc) + " " + str(var_runnable[loc].varValue))

    print("")
    print("##### WORKSHARE #####")
    sum_workload = 0
    for loc in var_workshare.keys():
        print(str(loc) + " " + str(var_workshare[loc].varValue))
        sum_workload += var_workshare[loc].varValue

    print("Sum Workload: "+str(sum_workload))

    return




def main():
    param_num_fragments = 7
    param_num_queries = 7
    param_num_nodes = 4

    param_fragment_size = random.sample(range(1, 100), param_num_fragments)
    param_queries = generate_queries(param_num_queries, param_num_fragments)
    param_query_frequency = random.sample(range(1, 100), param_num_queries)
    param_query_cost = random.sample(range(1, 100), param_num_queries)
    param_query_workload = [a * b for a, b in zip(param_query_frequency, param_query_cost)]
    param_total_workload = sum(param_query_workload)

    print(len(param_queries))
    print(len(param_query_cost))

    solve_split(param_fragment_size, param_queries, param_query_frequency, param_query_cost, param_num_nodes)

if __name__ == '__main__':
    main()