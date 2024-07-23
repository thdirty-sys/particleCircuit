class Node:
    def __init__(self, start_pos, rate):
        self.pos = start_pos
        self.rate = rate


class Particle:
    """General element of the Circuit"""
    def __init__(self, start_pos):
        self.pos = start_pos

class Repository:
    """Repository object; fed particles."""
    def __init__(self, start_pos, capacity):
        self.capacity = capacity
        self.pos = start_pos
        self.count = 0

class Circuit:
    """The circuit, with all its received features. Must have/generate paths to be functional.
    Given entry/exit nodes necessary, as well as repositories."""
    def __init__(self, repos, ingress, egress):
        self.repos = repos
        self.entry_nodes = ingress
        self.exit_nodes = egress
        self.path = []
        self.particles = []

    def gen_path(self):
        pass




