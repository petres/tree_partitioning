"""Implement rooted trees with weights on leaves. Weight of non-leaf vertices
are defined by the weight of their children.

Our goal is to create an arbitrary rooted tree with positive weighted leaves
and to partition the tree into equally weighted subtrees, that is a set of
subtrees such that the leaves of each subtree have approximately equal weight
and form a partition of all leaves of the original tree. Since there might not
be an exact solution, the algorithm tries to minimize the squared error for a
given target weight for each of the subtrees."""


# how many spaces indent for printing tree
INDENT = 4


def norm(value):
    return value**2


class Tree(object):
    """This is quite a useless container class. Turned out that working only
    with nodes is easier."""

    def __init__(self, root):
        self.root = root

    def get_nodes(self, subtree_root=None):
        """Get all nodes from subtree with root ``subtree_root`` or all nodes
        if ``subtree_root`` not given."""
        if subtree_root is None:
            subtree_root = self.root
        return [subtree_root] + [node for child in subtree_root.children
                                 for node in self.get_nodes(child)]


class Node(object):
    """Representing one vertex in the tree. Since the vertex knows about its
    children, objects of this type can be used to represent the whole
    subtree."""

    def __init__(self, weight=None):
        self.weight = weight
        self.children = []
        self.parent = None
        self.child_order = None  # assuming plane tree: self is n-th child

    def add_child(self, child):
        """Modifies child!"""
        child.parent = self
        child.child_order = len(self.children) + 1
        self.children.append(child)

    def path_to_root(self):
        if self.parent is None:
            # self is root
            return []
        return [self.child_order] + self.parent.path_to_root()

    def path_from_root(self):
        return reversed(self.path_to_root())

    def subtree_by_path(self, path):
        """``path`` is list of int (order of children along path)."""
        if len(path) == 0:
            return self
        child = self.children[path[0]]
        return child.subtree_by_path(path[1:])

    def __str__(self):
        path_from_root_str = ["root"]
        path_from_root_str += [str(order) for order in self.path_from_root()]
        return "[{}]".format(" -> ".join(path_from_root_str))

    def is_leaf(self):
        return len(self.children) == 0

    def _print_subtree(self, height):
        indent = ("|" + " " * (INDENT-1)) * height
        node_str = indent + "|\n" + indent + "-" * INDENT + "+ "
        if self.weight is not None:
            node_str += str(self.weight)
        print(node_str)
        for child in self.children:
            child._print_subtree(height + 1)

    def print_subtree(self):
        """Do not use with too large trees."""
        self._print_subtree(height=0)

    def calc_subtree_weights(self):
        if self.weight is None:  # not a leaf
            self.weight = 0.
            for child in self.children:
                child.calc_subtree_weights()
                self.weight += child.weight
        return self.weight

    def weight_error(self, target_weight):
        return norm(target_weight - self.weight)

    def find_partition(self, target_weight):
        """Return list of subtrees with approximate weight target_weight and
        weight error. The subtrees form a partition of the tree
        (:<==> each leaf of self is node in exactly one subtree) and sum of
        squared weight errors is minimized."""
        if not target_weight > 0.:
            raise ValueError("{} invalid target_weight, must be >0".format(
                target_weight))
        if self.weight is None:
            raise RuntimeError(
                "No weight calculated for node {}, run "
                "root.calc_subtree_weights() first".format(self))

        children = self.children  # make it short
        # Question:
        # is self a better approximation to target_weight than children?
        # Or:  ||self.weight - target_weight||
        #         < sum(||child.weight - target_weight|| for child in children)
        # ...for some norm ||.||
        if len(children) == 0:
            # no children at all
            return self.weight_error(target_weight), [self]

        if self.weight <= target_weight:
            # already too small, children have even smaller weight
            return self.weight_error(target_weight), [self]

        results_children = [child.find_partition(target_weight)
                            for child in children]
        weight_error_children = sum([weight_error for weight_error, subtrees in
                                     results_children])
        # flatten it...
        partition_children = [subtree for weight_error, subtrees in
                               results_children for subtree in subtrees]

        # this is correct, but useless...
        #if max([child.weight for child in children]) >= target_weight:
        #    # all children have too large weight, self definitely too large
        #    return weight_error_children, partition_children

        # there is at least one child with child.weight < target_weight
        if self.weight_error(target_weight) <= weight_error_children:
            return self.weight_error(target_weight), [self]
        else:
            return weight_error_children, partition_children


def generate_random_tree(height, avg_degree):
    weight = None if height > 1 else 1.  # only leaves get weight
    root = Node(weight)
    if height > 1:
        for i in range(avg_degree):
            root.add_child(generate_random_tree(height - 1, avg_degree).root)

    return Tree(root)
