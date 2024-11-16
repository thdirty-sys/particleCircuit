
from circuitOperations.circuitObjects import *
import numpy as np

class TasepCircuitDispatcher():
    """Specialised dispatcher for a circuit under TASEP (Totally Asymmetric Simple Exclusion Process)"""
    def __init__(self):
        self.lock = None
        self.circuit = None
        self.hidden = None
        self.highlighted_pos = None
        self.return_handler = None
        self.tracked = []


    def run_tasep(self):
        """"TASEP dispatcher modified for dearpygui"""

        rng = np.random.default_rng()
        self.play_time = 0
        self.particle_count = 0

        # Shorthand
        c = self.circuit
        while self.particle_count < 10000:
            option_size = len(c.entry_nodes) + len(c.particles)
            self.play_time += rng.exponential(1/option_size)
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
                            chosen.count += 1
                            self.particle_count += 1
                            chosen.take(self.play_time)

            if chosen.name == "particle":
                # If in exit node we take off the circuit with p. rate
                for ex in c.exit_nodes:
                    if ex.pos == chosen.pos:
                        if rng.random() <= -ex.rate:
                            self.circuit.particles.remove(chosen)
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
                        for n in self.circuit.body:
                            if n.pos == next_pos:
                                n.count += 1
                                n.take(self.play_time)
                                break

    def pos_empty(self, pos, ori):
        for p in self.circuit.particles:
            if p.pos == pos:
                if ori == p.orientation:
                    return False
        else:
            return True



