import functools
import operator

import anytree
from anytree import LevelOrderIter, RenderTree, DoubleStyle
from sympy.ntheory import factorint
import math
from anytree.exporter import DotExporter

from solver_node import SolverNode

def add_split_ratios(root: SolverNode):
    [node.set_split_ratio() for node in LevelOrderIter(root)]

def design_node(node):
    return "shape=box"

def label_edges(node, child):
    return 'label='+str(round(node.split_ratio[node.children.index(child)], 2))


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
    add_split_ratios(parent)
    number_tree_nodes(parent)
    number_tree_nodes(parent)
    DotExporter(parent, name="PrimeFactorGraph", nodeattrfunc=design_node,
                edgeattrfunc=label_edges).to_picture("abc.png")
    return parent


def binary_tree(nr_leaf_nodes):
    assert math.log2(nr_leaf_nodes).is_integer(), "Number of leaves needs to be devidable by a " \
                                                  "power of 2"
    parent = SolverNode("Root Binary")
    nr_children = int(math.log2(nr_leaf_nodes))
    children = [2] * nr_children
    append(parent, children)
    add_split_ratios(parent)
    number_tree_nodes(parent)
    DotExporter(parent, name="Binary", nodeattrfunc=design_node, edgeattrfunc=label_edges).to_picture("abc.png")
    return parent


def one_split_tree(nr_leaf_nodes, should_squeeze=True, use_normed=False):
    parent = SolverNode("Root One Split", should_squeeze, use_normed)
    append(parent, [nr_leaf_nodes])
    add_split_ratios(parent)
    number_tree_nodes(parent)
    DotExporter(parent, name="OneSplitGraph", nodeattrfunc=design_node, edgeattrfunc=label_edges).to_picture("abc.png")
    return parent



def one_vs_all_split(nr_leaf_nodes):
    parent = SolverNode("Root One Vs All Split")
    parent.split_ratio = [1/nr_leaf_nodes, 1 - (1/nr_leaf_nodes)]
    previous_level_node = parent
    for i in range(1, nr_leaf_nodes):
        one = SolverNode('OneSide_' + str(i), parent=previous_level_node)
        all = SolverNode('AllSide_' + str(i), parent=previous_level_node)
        if not i == nr_leaf_nodes-1:
            all.split_ratio = [1/(nr_leaf_nodes-i), 1 - (1/(nr_leaf_nodes-i))]
        previous_level_node = all
    number_tree_nodes(parent)
    DotExporter(parent, name="OneVsAllGraph", nodeattrfunc=design_node, edgeattrfunc=label_edges).to_picture("abc.png")
    return parent


def append(parent, splits):
    if not splits:
        return
    for i in range(splits[0]):
        n = SolverNode('l_' + str(len(splits)) + '_n_' + str(i), parent=parent)
        append(n, splits[1:])


def approximate_tree(nr_leaves, split):
    root = SolverNode("Approx: " + str(split))
    parents_stack = [root]
    while len(root.leaves) != nr_leaves:
        while parents_stack:
            missing_leaves = nr_leaves - len(root.leaves) + 1 # plus 1 because we loose the leave
            # we are currently working on if we add new leaves
            parent = parents_stack.pop(0)
            do_split = split if split <= missing_leaves else missing_leaves
            if do_split <= 1:
                break
            append(parent, [do_split])
        parents_stack = list(root.leaves)
    #print_tree(root)
    add_split_ratios(root)
    number_tree_nodes(root)
    DotExporter(root, name="AproximateGraph", nodeattrfunc=design_node, edgeattrfunc=label_edges).to_picture("abc.png")
    return root

def node_name(node:SolverNode):
    if not node.is_leaf:
        name = node.name
    else:
        path_split = [p.name for p in node.path]
        if len(path_split) > 2:
            name = str(path_split[-2:])
        else:
            name = node.name
    return name

def number_tree_nodes(root:SolverNode):
    depth = 0
    count = 0
    for num, node in enumerate(LevelOrderIter(root)):
        if node.is_root:
            continue
        if node.depth > depth:
            count = 0
            depth = node.depth

        node.name = str(depth) + '_' + str(count)
        count += 1

def dot_export_actuall_workload(root: SolverNode):
    def label_split(node, child):
        should = 'label=' + str(round(node.split_ratio[node.children.index(child)], 2))
        has = node.workshare_split


    DotExporter(root, nodeattrfunc=design_node,
                edgeattrfunc=label_split).to_picture(root.name+".png")



def print_tree(root):
    print(RenderTree(root, style=DoubleStyle))


