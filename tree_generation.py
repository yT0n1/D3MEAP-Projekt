import functools
import operator

from sympy.ntheory import factorint
import math

from solver_node import SolverNode


def prime_factor_tree(nr_leaf_nodes, reverse=False, combine=False):
    tuples = factorint(nr_leaf_nodes).items()
    if combine:
        if len(tuples) == 1:
            # if we only have one prime number doing the power of it will be the exact same as the
            # default split, thus we leave one out
            prime, times = list(tuples)[0]
            split_list = [prime ** (times - 1), prime]
        else:
            split_list = [prime ** times for prime, times in tuples]
    else:
        split_list = [[prime] * times for prime, times in tuples]
        split_list = functools.reduce(operator.iconcat, split_list, [])
    split_list.sort(reverse=reverse)
    parent = SolverNode("Root Prime " + str(split_list))
    append(parent, split_list)
    return parent


def binary_tree(nr_leaf_nodes):
    assert math.log2(nr_leaf_nodes).is_integer(), "Number of leaves needs to be devidable by a " \
                                                  "power of 2"
    parent = SolverNode("Root Binary")
    nr_children = int(math.log2(nr_leaf_nodes))
    children = [2] * nr_children
    append(parent, children)
    return parent


def one_split_tree(nr_leaf_nodes):
    parent = SolverNode("Root One Split")
    append(parent, [nr_leaf_nodes])
    return parent


def append(parent, splits):
    if not splits:
        return
    for i in range(splits[0]):
        n = SolverNode('l_' + str(len(splits)) + '_n_' + str(i), parent=parent)
        append(n, splits[1:])
