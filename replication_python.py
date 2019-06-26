from pulp import *
import random


def generate_index_dict(first_index, second_index):
    dict_index = []
    for i in range(first_index):
        for j in range(second_index):
            dict_index.append((i, j))
    return dict_index


def generate_queries():
    queries = []
    for i in range(param_num_fragments):
        temp_list = []
        for j in range(param_num_queries):
            temp_list.append(random.choice([0, 1]))
        queries.append(temp_list)
    return queries


def objective():
    sum = 0
    for f in range(param_num_fragments):
        for n in range(param_num_nodes):
            sum += var_location[(f,n)] * param_fragment_size[f]
    return sum


def nb_1(problem):
    for q in range(param_num_queries):
        c = sum([var_runnable[q,n] for n in range(param_num_nodes)]) >= 1
        problem += c
    return problem

def nb_2(problem):
    for q in range(param_num_queries):
        c = sum([var_workshare[q,n] for n in range(param_num_nodes)]) >= 1
        problem += c
    return problem

def nb_3(problem):
    for q in range(param_num_queries):
        c = sum([var_workshare[q,n] for n in range(param_num_nodes)]) >= 1
        problem += c
    return problem


problem = LpProblem("replication", LpMinimize)

param_num_fragments = 8
param_num_queries = 9
param_num_nodes = 4
param_num_servers = param_num_nodes * 3

param_fragment_size = random.sample(range(1, 100), param_num_fragments)
param_queries = generate_queries()
param_query_frequency = random.sample(range(1, 100), param_num_queries)
param_query_cost = random.sample(range(1, 100), param_num_queries)
param_query_workload = [a*b for a,b in zip(param_query_frequency, param_query_cost)]
param_total_workload = sum(param_query_workload)

param_servers_per_node = param_num_servers / param_num_nodes

location_dict_index = generate_index_dict(param_num_fragments, param_num_nodes)
runnable_dict_index = generate_index_dict(param_num_queries, param_num_nodes)
workshare_dict_index = generate_index_dict(param_num_queries, param_num_nodes)

var_location = LpVariable.dicts(name="location", indexs=location_dict_index, lowBound=0, upBound=1, cat='Integer')
var_runnable = LpVariable.dicts(name="runnable", indexs=runnable_dict_index, lowBound=0, upBound=1, cat='Integer')
var_workshare = LpVariable.dicts(name="workshare", indexs=workshare_dict_index, lowBound=0, cat='Continuous')

problem += objective()
problem = nb_1(problem)
problem = nb_2(problem)

print(problem)
problem.solve()

print("")
print("##### LOCATION #####")
for loc in var_location.keys():
    print(var_location[loc].varValue)

print("")
print("##### RUNNABLE #####")
for loc in var_runnable.keys():
    print(var_runnable[loc].varValue)

print("")
print("##### WORKSHARE #####")
for loc in var_workshare.keys():
    print(var_workshare[loc].varValue)
