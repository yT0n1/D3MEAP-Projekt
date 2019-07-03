import anytree
from anytree import RenderTree


class Observation:
    def __init__(self, space, time, tree:anytree, aborted):
        self.tree = tree
        self.time = time
        self.space = space
        self.aborted = aborted

    def __str__(self):
        return '\nSpace: {}, Time: {}, WasAborted: {}\n{}\n'.format(self.space, self.time,
                                                                self.aborted, RenderTree(self.tree))