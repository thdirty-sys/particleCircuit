import time
from circuitOperations.particleObjs import *
import numpy as np
import dearpygui.dearpygui as dpg


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


class TasepCircuitDispatcher(CircuitDispatcher):
    """Specialised dispatcher for a circuit under TASEP (Totally Asymmetric Simple Exclusion Process)"""

    def run_tasep(self):
        rng = np.random.default_rng()

        if self.circuit is None:
            print("No circuit has been generated")
            return None

        # Shorthand
        c = self.circuit

        while not c.complete():
            # Pick entry node or active particle randomly
            chosen = rng.choice(c.entry_nodes + c.particles)

            # Deals with case of entry node
            if chosen.name == "node":
                # Creates particle if empty with probability according to rate of node
                if self.pos_empty(chosen.pos, c.particles):
                    # With probability of node rate
                    if rng.random() <= chosen.rate:
                        c.particles.append(Particle(chosen.pos))

            if chosen.name == "particle":
                if c.in_exit_node(chosen.pos):
                    c.particles.remove(chosen)
                else:
                    beginning = c.in_repo(chosen.pos) or c.in_entry_node(chosen.pos)
                    if chosen.orientation == c.path_orientation[chosen.pos] or beginning:
                        next_pos = tuple(rng.choice(c.path_space[chosen.pos]))
                        if chosen.pos in c.splits:
                            if next_pos in c.splits[chosen.pos]:
                                chosen.orientation = c.path_orientation[next_pos]
                    else:
                        next_pos = c.undercurrent_space[chosen.pos]
                    if self.pos_empty(next_pos, chosen.orientation):
                        chosen.pos = next_pos

    def pos_empty(self, pos, ori):
        for p in self.circuit.particles:
            if p.pos == pos:
                if ori == p.orientation:
                    return False
        else:
            return True


class TasepCircuitDispatcherGUI(TasepCircuitDispatcher):

    def display_currents(self):
        en = self.circuit.entry_nodes[0]
        ex = self.circuit.exit_nodes[0]
        if en.count != 0:
            dpg.configure_item("en_node_current0",
                               default_value="Current: "+str(round(len(en.check_in)/(self.play_time - en.check_in[0]), 3))+"p/s")

        if ex.count != 0:
            dpg.configure_item("ex_node_current0",
                               default_value="Current: "+str(round(len(ex.check_in)/(self.play_time - ex.check_in[0]), 3))+"p/s")

        for i, repo in enumerate(self.circuit.repos):
            if repo.count != 0:
                dpg.configure_item("repo_current" + str(i),
                                   default_value="Current: "+str(round(len(repo.check_in) / (self.play_time - repo.check_in[0]), 3)) + "p/s")


    def run_tasep(self):
        """"TASEP dispatcher modified for dearpygui"""

        rng = np.random.default_rng()
        self.run = True
        self.alive = True
        self.speed_factor = 1
        self.debug_particle = False

        if self.circuit is None:
            print("No circuit has been generated")
            return None

        # Shorthand
        c = self.circuit
        particle_count = 0
        self.play_time = 0
        while not c.complete() and self.alive:
            while self.run:
                option_size = len(c.entry_nodes) + len(c.particles)
                wait_factor = rng.exponential(1/(self.speed_factor*option_size))
                self.play_time += rng.exponential(1/(option_size))
                time.sleep(wait_factor)
                # Pick entry node or active particle randomly
                chosen = rng.choice(c.entry_nodes + c.particles)

                # Deals with case of entry node
                if chosen.name == "node":
                    # Creates particle if empty with probability according to rate of node
                    if self.pos_empty(chosen.pos, c.particles):
                        # With probability of node rate
                        if self.pos_empty(chosen.pos, "-"):
                            if rng.random() <= chosen.rate:
                                new_particle = Particle(chosen.pos, particle_count)
                                new_particle.orientation = "-"
                                c.particles.append(new_particle)
                                if particle_count % 10 == 0 and self.debug_particle:
                                    col = (255, 100, 0)
                                else:
                                    col = (255, 255, 255)
                                dpg.draw_circle(chosen.pos, 0.3, fill=col, parent="main_grid",
                                                tag="particle" + str(new_particle.no))
                                particle_count += 1
                                chosen.count += 1
                                chosen.take(self.play_time)

                if chosen.name == "particle":
                    #If in exit node we take off the circuit with p. rate
                    if c.in_exit_node(chosen.pos):
                        if rng.random() <= -c.exit_nodes[0].rate:
                            c.particles.remove(chosen)
                            dpg.delete_item("particle" + str(chosen.no))
                    else:
                        # Find next site to hop to
                        next_orientation = chosen.orientation
                        if next_orientation == c.path_orientation[chosen.pos]:
                            next_pos = tuple(rng.choice(c.path_space[chosen.pos]))
                            # Changing path at split
                            if next_pos not in c.undercurrent_space:
                                next_orientation = c.path_orientation[next_pos]

                        else:
                            next_pos = c.undercurrent_space[chosen.pos]

                        if c.in_repo(next_pos):
                            next_orientation = c.path_orientation[next_pos]
                        # Hop to site if unoccupied
                        if self.pos_empty(next_pos, next_orientation):
                            chosen.pos = next_pos
                            chosen.orientation = next_orientation
                            dpg.delete_item("particle" + str(chosen.no))
                            if chosen.orientation == c.path_orientation[next_pos] or c.in_exit_node(next_pos):
                                if chosen.no % 10 == 0 and self.debug_particle:
                                    col = (255, 100, 0)
                                else:
                                    col = (255, 255, 255)
                                dpg.draw_circle(next_pos, 0.3, fill=col, parent="main_grid",
                                                tag="particle" + str(chosen.no))
                            in_repo = c.in_repo(next_pos)
                            if in_repo or c.in_exit_node(next_pos):
                                for n in c.body:
                                    if n.pos == next_pos:
                                        n.count += 1
                                        n.take(self.play_time)
                                        if in_repo:
                                            dpg.configure_item("repo_text" + str(c.repos.index(n)), text = n.count)
                                        break
