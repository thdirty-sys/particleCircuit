from circuitOperations.particleObjs import *
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

        valid_repo_x = [i for i in range(2,48)]

        # Generate entry nodes w/ random positions and rates
        for n in range(rng.integers(1,2)): #high was 6
            new_node = Node((0, rng.integers(1,25)), rng.random())
            en_nodes.append(new_node)

        # Generate exit nodes w/ random positions and rates
        for n in range(rng.integers(1,2)): #high was 4
            new_node = Node((49, rng.integers(1,25)), -rng.random())
            ex_nodes.append(new_node)

        # Generate randomly placed repositories w/ random capacities
        for n in range(rng.integers(3,6)):
            chosen_x = rng.choice(valid_repo_x)
            new_repo = Repository((chosen_x, rng.integers(1,25)), rng.integers(100, 1001))
            # For convenience later, repos is ordered by x pos
            if repos is []:
                repos.append(new_repo)
            else:
                for i, repo in enumerate(repos):
                    if new_repo.pos[0] <= repo.pos[0]:
                        repos.insert(i, new_repo)
                        break
                else:
                    repos.append(new_repo)

            # To regulate distances between repositories
            valid_repo_x.remove(chosen_x)
            if chosen_x+1 in valid_repo_x:
                valid_repo_x.remove(chosen_x+1)
            if chosen_x-1 in valid_repo_x:
                valid_repo_x.remove(chosen_x-1)

        self.circuit = Circuit(repos, en_nodes, ex_nodes)
        return self.circuit


class TasepCircuitDispatcher(CircuitDispatcher):
    """Specialised dispatcher for a circuit under TASEP (Totally Asymmetric Simple Exclusion Process)"""

    def run_tasep(self):
        pass
