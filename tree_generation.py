import functools
import operator

from anytree import Node
from sympy.ntheory import factorint
import math

from solver_node import SolverNode


def prime_factor_tree(nr_leaf_nodes, reverse=False):
    prime_factors = factorint(nr_leaf_nodes)
    sort = sorted(prime_factors.items(),reverse=reverse)
    uncompressed = [[prime]*times for prime, times in sort]
    flat = functools.reduce(operator.iconcat, uncompressed, [])
    parent = SolverNode("Root Prime")
    append(parent, flat)
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
