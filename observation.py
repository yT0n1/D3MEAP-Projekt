import anytree
from anytree import RenderTree


class Observation:
    def __init__(self, space, time, tree:anytree, aborted, deviation, name, total_replication):
        self.tree = tree
        self.time = time
        self.space = space
        self.aborted = aborted
        self.deviation = deviation
        self.name = name
        self.total_replication = total_replication

    def __str__(self):
        return '\nName: {} \nSpace: {}, Time: {}, WasAborted: {}, Deviation: {}, Total Rep: {] \n{}\n'.format(self.name, self.space, self.time,
                                                                self.aborted, self.deviation, self.total_replication, RenderTree(self.tree))