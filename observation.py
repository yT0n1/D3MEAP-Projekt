import anytree
from anytree import RenderTree


class Observation:
    def __init__(self, space, time, tree:anytree, aborted, deviation):
        self.tree = tree
        self.time = time
        self.space = space
        self.aborted = aborted
        self.deviation = deviation

    def __str__(self):
        return '\nSpace: {}, Time: {}, WasAborted: {}, Deviation: {} \n{}\n'.format(self.space, self.time,
                                                                self.aborted, self.deviation, RenderTree(self.tree))