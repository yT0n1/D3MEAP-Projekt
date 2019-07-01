import random


def generate_queries(param_num_queries, param_num_fragments):
    queries = []
    for i in range(param_num_queries):
        temp_list = []
        for j in range(param_num_fragments):
            temp_list.append(random.choice([0, 1]))
        queries.append(temp_list)
    return queries


def print_location(var, index_x, index_y, cast_to_int=True):
    for n in range(index_x):
        print_string = "Node " + str(n) + ": "
        for f in range(index_y):
            if cast_to_int:
                print_string += str(int(var[(f, n)].varValue)) + " "
            else:
                print_string += "{0:.5f} ".format(round(var[(f, n)].varValue, 5))
        print(print_string)
    print(" ")


def print_location_adaptive(var, index_x, indeces, cast_to_int=True):
    header = " " * 7
    if cast_to_int:
        space = " "
    else:
        space = " " * 7
    for index in indeces:
        header += space + str(index)
    print(header)
    for n in range(index_x):
        print_string = "Node " + str(n) + ": "
        for f in indeces:
            if cast_to_int:
                print_string += str(int(var[(f, n)].varValue)) + " "
            else:
                print_string += "{0:.5f} ".format(round(var[(f, n)].varValue, 5))
        print(print_string)
    print(" ")