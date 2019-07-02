import functools
import operator

from anytree import Node
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
            split_list = [prime**(times-1), prime]
        else:
            split_list = [prime**times for prime, times in tuples]
    else:
        split_list = [[prime]*times for prime, times in tuples]
        split_list = functools.reduce(operator.iconcat, split_list, [])
    split_list.sort(reverse=reverse)
    parent = SolverNode("Root Prime " + str(split_list))
    append(parent, split_list)
    return parent

def binary_tree(nr_leaf_nodes):
    assert math.log2(nr_leaf_nodes).is_integer() == True
    parent = SolverNode("Root Binary")
    nr_children = int(math.log2(nr_leaf_nodes))
    children = [2] * nr_children
    append(parent, children)
    return parent


def append(parent, future_children):
    if not future_children:
        return
    for i in range(future_children[0]):
        n = SolverNode('l_'+str(len(future_children))+'_n_'+str(i), parent=parent)
        append(n, future_children[1:])
