from particleObj import *
import numpy as np

class CircuitDispatcher:
    """General Circuit dispatcher class."""

    def __init__(self):
        self.circuit = None

    def gen_circuit(self):
        """Generate circuit, including nodes, paths, repositories. Path generated within circuit."""
        rng = np.random.default_rng()
        en_nodes = []
        ex_nodes = []
        repos = []


        # Generate entry nodes w/ random positions and rates
        for n in range(rng.integers(1,6)):
            new_node = Node((0, rng.integers(1,25)), rng.random())
            en_nodes.append(new_node)

        # Generate exit nodes w/ random positions and rates
        for n in range(rng.integers(1,4)):
            new_node = Node((49, rng.integers(1,25)), -rng.random())
            ex_nodes.append(new_node)

        # Generate randomly placed repositories w/ random capacities
        for n in range(rng.integers(2,6)):
            new_repo = Repository((rng.integers(2,48), rng.integers(1,25)), )
            repos.append(new_repo)

        self.circuit = Circuit(repos, en_nodes, ex_nodes)
        self.circuit.gen_path()


class TasepCircuitDispatcher(CircuitDispatcher):
    """Specialised dispatcher for a circuit under TASEP (Totally Asymmetric Simple Exclusion Process)"""

    def run_tasep(self):
        pass
