import time
from circuitOperations.particleObjs import *
import numpy as np
import dearpygui.dearpygui as dpg

class TasepCircuitDispatcher():
    """Specialised dispatcher for a circuit under TASEP (Totally Asymmetric Simple Exclusion Process)"""
    def __init__(self):
        self.circuit = None
        self.hidden = None
        self.highlighted_pos = None
        self.return_handler = None
        self.coords = False

    def gen_circuit(self):
        """Generate circuit, including nodes, paths, repositories. Path generated within circuit."""
        rng = np.random.default_rng()
        en_nodes = []
        ex_nodes = []
        repos = []

        valid_repo_x = [i for i in range(2, 48)]

        # Generate entry nodes w/ random positions and rates
        for n in range(rng.integers(1, 2)):  # high was 6
            new_node = Node((0, int(rng.integers(1, 25))), rng.random())
            en_nodes.append(new_node)

        # Generate exit nodes w/ random positions and rates
        for n in range(rng.integers(1, 2)):  # high was 4
            new_node = Node((49, int(rng.integers(1, 25))), -rng.random())
            ex_nodes.append(new_node)

        # Generate randomly placed repositories w/ random capacities
        for n in range(rng.integers(3, 7)):
            chosen_x = int(rng.choice(valid_repo_x))
            new_repo = Repository((chosen_x, int(rng.integers(1, 25))), int(rng.integers(100, 1001)))
            # For convenience later, repos is ordered by x pos. Following code sorts list.
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
            if chosen_x + 1 in valid_repo_x:
                valid_repo_x.remove(chosen_x + 1)
            if chosen_x - 1 in valid_repo_x:
                valid_repo_x.remove(chosen_x - 1)

        self.circuit = Circuit(repos, en_nodes, ex_nodes)
        return self.circuit

    def run_tasep(self):
        """"TASEP dispatcher modified for dearpygui"""

        rng = np.random.default_rng()
        self.run_init()

        if self.circuit is None:
            print("No circuit has been generated")
            return None

        # Shorthand
        c = self.circuit
        while not c.complete() and self.alive:
            while self.run:
                option_size = len(c.entry_nodes) + len(c.particles)
                wait_factor = rng.exponential(1 / (self.speed_factor * option_size))
                self.play_time += rng.exponential(1 / (option_size))
                time.sleep(wait_factor)
                # Pick entry node or active particle randomly
                chosen = rng.choice(c.entry_nodes + c.particles)

                # Deals with case of entry node
                if chosen.name == "node":
                    # Creates particle if empty with probability according to rate of node
                    if self.pos_empty(chosen.pos, c.particles):
                        # With probability of node rate add new particle to empty node
                        if rng.random() <= chosen.rate:
                            if self.pos_empty(chosen.pos, c.path_orientation[chosen.pos]):
                                new_particle = Particle(chosen.pos, self.particle_count)
                                new_particle.orientation = c.path_orientation[chosen.pos]
                                c.particles.append(new_particle)
                                self.entry_handle(chosen)

                if chosen.name == "particle":
                    # If in exit node we take off the circuit with p. rate
                    for ex in c.exit_nodes:
                        if ex.pos == chosen.pos:
                            if rng.random() <= -ex.rate:
                                self.exit_handle(chosen)
                            break
                    else:
                        ori = chosen.orientation
                        # The following calculates the next pos.
                        # If not in undercurrent, next pos is randomly selected. Otherwise it is determinate.
                        # Case when chosen particle is NOT in undercurrent
                        if chosen.orientation == c.path_orientation[chosen.pos]:
                            next_pos = tuple(rng.choice(c.path_space[chosen.pos]))
                            # If next pos is not undercurrent pos, then change ori since we have split
                            if next_pos not in c.undercurrent_space:
                                ori = c.path_orientation[next_pos]
                            # If next pos IS undercurrent, but the undercurrent is not of the correct orientation
                            # do the same.
                            elif ori != c.undercurrent_orientation[next_pos]:
                                ori = c.path_orientation[next_pos]
                        # Case when chosen particle IS in undercurrent
                        else:
                            next_pos = c.undercurrent_space[chosen.pos]

                        if c.in_repo(next_pos):
                            ori = c.path_orientation[next_pos]
                        # Hop to site if unoccupied
                        if self.pos_empty(next_pos, ori):
                            chosen.pos = next_pos
                            chosen.orientation = ori
                            self.hop_handle(chosen, next_pos)

    def hop_handle(self, chosen, next_pos):
        dpg.delete_item("particle" + str(chosen.no))
        if chosen.orientation == self.circuit.path_orientation[next_pos] or self.circuit.in_exit_node(next_pos):
            if chosen.no % 10 == 0 and self.debug_particle:
                col = (255, 100, 0)
            else:
                col = (255, 255, 255)
            dpg.draw_circle(next_pos, 0.3, fill=col, parent="main_grid",
                            tag="particle" + str(chosen.no))
        in_repo = self.circuit.in_repo(next_pos)
        for n in self.circuit.body:
            if n.pos == next_pos:
                n.count += 1
                n.take(self.play_time)
                if n.name == "repo":
                    dpg.configure_item(f"repo_text_{n.pos}", text=n.count)
                break

    def exit_handle(self, chosen):
        self.circuit.particles.remove(chosen)
        dpg.delete_item("particle" + str(chosen.no))

    def entry_handle(self, chosen):
        chosen.count += 1
        chosen.take(self.play_time)

    def pos_empty(self, pos, ori):
        for p in self.circuit.particles:
            if p.pos == pos:
                if ori == p.orientation:
                    return False
        else:
            return True

    def run_init(self):
        self.run = True
        self.alive = True
        self.speed_factor = 1
        self.debug_particle = False
        self.particle_count = 0
        self.play_time = 0


