import functools
import operator
from statistics import mean

import math
from anytree import LevelOrderIter, RenderTree, DoubleStyle
from anytree.exporter import DotExporter
from sympy.ntheory import factorint

from core_functionality.solver_node import SolverNode


def add_split_ratios(root: SolverNode):
    [node.set_split_ratio() for node in LevelOrderIter(root)]


def design_node(node):
    return "shape=box"


def label_edges(node, child):
    return 'label=' + str(round(node.split_ratio[node.children.index(child)], 2))


def prime_factor_tree(nr_leaf_nodes, reverse=False, combine=False):
    tuples = factorint(nr_leaf_nodes).items()
    if combine:
        if len(tuples) == 1 and list(tuples)[0][1] != 1:
            # if we only have one prime number doing the power of it will be the exact same as the
            # default split, thus we leave one out, unless the number is a prime number itself
            prime, times = list(tuples)[0]
            split_list = [prime ** (times - 1), prime]
        else:
            split_list = [prime ** times for prime, times in tuples]
    else:
        split_list = [[prime] * times for prime, times in tuples]
        split_list = functools.reduce(operator.iconcat, split_list, [])
    split_list.sort(reverse=reverse)
    name = ''
    name += ' combined' if combine else ''
    name += ' reversed' if reverse else ''
    parent = SolverNode("Prime " + name + '|' + str(split_list))
    append(parent, split_list)
    add_split_ratios(parent)
    number_tree_nodes(parent)
    return parent


def binary_tree(nr_leaf_nodes):
    assert math.log2(nr_leaf_nodes).is_integer(), "Number of leaves needs to be devidable by a " \
                                                  "power of 2"
    parent = SolverNode("Binary")
    nr_children = int(math.log2(nr_leaf_nodes))
    children = [2] * nr_children
    append(parent, children)
    add_split_ratios(parent)
    number_tree_nodes(parent)
    return parent


def one_split_tree(nr_leaf_nodes, use_normed=False):
    parent = SolverNode("Complete", use_normed)
    append(parent, [nr_leaf_nodes])
    add_split_ratios(parent)
    number_tree_nodes(parent)
    return parent


def one_vs_all_split(nr_leaf_nodes):
    parent = SolverNode("One Vs All Split")
    parent.split_ratio = [1 / nr_leaf_nodes, 1 - (1 / nr_leaf_nodes)]
    previous_level_node = parent
    for i in range(1, nr_leaf_nodes):
        one = SolverNode('OneSide_' + str(i), parent=previous_level_node)
        all = SolverNode('AllSide_' + str(i), parent=previous_level_node)
        if not i == nr_leaf_nodes - 1:
            all.split_ratio = [1 / (nr_leaf_nodes - i), 1 - (1 / (nr_leaf_nodes - i))]
        previous_level_node = all
    number_tree_nodes(parent)
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
            missing_leaves = nr_leaves - len(root.leaves) + 1  # plus 1 because we loose the leave
            # we are currently working on if we add new leaves
            parent = parents_stack.pop(0)
            do_split = split if split <= missing_leaves else missing_leaves
            if do_split <= 1:
                break
            append(parent, [do_split])
        parents_stack = list(root.leaves)
    # print_tree(root)
    add_split_ratios(root)
    number_tree_nodes(root)
    return root


def number_tree_nodes(root: SolverNode):
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


def dot_export_actual_workload(root: SolverNode, name_appendix=''):
    def label_split(node, child):
        should = str(round(node.split_ratio[node.children.index(child)], 2))
        if node.workshare_split:
            has = str(round(mean(ws[node.children.index(child)] for ws in node.workshare_split), 2))
        else:
            has = "-"
        return 'label="' + should + ' | ' + has + '"'

    file_name = "tree_images/" + root.name + name_appendix + ".png"
    file_name = file_name.replace("|", "_")

    DotExporter(root, nodeattrfunc=design_node,
                edgeattrfunc=label_split).to_picture(file_name)

def dot_export_ideal_workload(root: SolverNode, name_appendix=''):
    def label_split(node, child):
        should = str(round(node.split_ratio[node.children.index(child)], 2))
        return 'label="' + should + '"'

    DotExporter(root, nodeattrfunc=design_node,
                edgeattrfunc=label_split, options=['dpi=300']).to_picture(root.name +
                                                                           name_appendix + ".png")

def print_tree(root):
    print(RenderTree(root, style=DoubleStyle))


if __name__ == '__main__':
    trees_8 = [approximate_tree(6,2),approximate_tree(6,3), approximate_tree(6,4),
               approximate_tree(6,5),
               prime_factor_tree(6,True), prime_factor_tree(6,False), one_vs_all_split(6),
               one_split_tree(6)]
    for tree in trees_8:
        dot_export_ideal_workload(tree)