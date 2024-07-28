import numpy as np
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

    def in_column_entry_space(self, x):
        if self.pos[0] == x:
            return True
        else:
            return False


class Circuit:
    """The circuit, with all its received features. Must have/generate paths to be functional.
    Given entry/exit nodes necessary, as well as repositories."""
    def __init__(self, repos, ingress, egress):
        self.repos = repos
        self.entry_nodes = ingress
        self.exit_nodes = egress
        self.path_space = {}
        for y in range(26):
            for x in range(50):
                self.path_space[(x,y)] = []
        self.particles = []

    def gen_circuit_paths(self):
        rng = np.random.default_rng()

        # Generate first, necessary path
        self.path_find(self.entry_nodes[0].pos, self.repos[0].pos)

        # Select number of nodes to be attached to first branch binomially
        available = self.repos[1:]
        no_available = len(available)
        no_selected = rng.binomial(no_available, 1/no_available)
        selected = rng.choice(available, no_selected)

        pointer_pos = self.entry_nodes[0].pos
        print(self.path_space[pointer_pos])
        for repo in selected:
            pointer_pos = self.path_space[self.path_space[pointer_pos][0]]
            print(pointer_pos, repo.pos)
            if pointer_pos == repo.pos or pointer_pos[0] > repo.pos[0]:
                break
            else:
                self.path_find(pointer_pos, repo.pos)




    def path_find(self, start, target):
        target_x, target_y = target
        start_x, start_y = start
        found = False

        # Construct path
        l_supplement = 0
        u_supplement = 0

        # Split into cases depending on whether start is above or below
        if target_y > start_y:
            while l_supplement != start_y or target_y + u_supplement != 26:
                pos_sketch_lower = [start, (start_x, start_y-l_supplement), (target_x,start_y-l_supplement), target]
                if self.path_check(pos_sketch_lower):
                    self.gen_path(pos_sketch_lower)
                    found = True
                    break
                else:
                    l_supplement += 1

                pos_sketch_higher = [start, (start_x, target_y+u_supplement), (target_x, target_y+u_supplement), target]
                if self.path_check(pos_sketch_higher):
                    self.gen_path(pos_sketch_higher)
                    found = True
                    break
                else:
                    u_supplement += 1
        else:
            while target_y != l_supplement or start_y + u_supplement != 26:
                pos_sketch_lower = [start, (start_x, target_y - l_supplement), (target_x, target_y - l_supplement), target]
                if self.path_check(pos_sketch_lower):
                    self.gen_path(pos_sketch_lower)
                    found = True
                    break
                else:
                    l_supplement += 1

                pos_sketch_higher = [start, (start_x, start_y + u_supplement), (target_x, start_y + u_supplement), target]
                if self.path_check(pos_sketch_higher):
                    self.gen_path(pos_sketch_higher)
                    found = True
                    break
                else:
                    u_supplement += 1
        return found


    def gen_path(self, path_sketch):
        # Draws paths between each corner and adds it to path space
        for i in range(1, len(path_sketch)):
            prev_x, prev_y = path_sketch[i-1]
            next_x, next_y = path_sketch[i]
            if next_x != prev_x:
                for x in range(prev_x, next_x):
                    self.path_space[(x, prev_y)].append((x+1, prev_y))
            else:
                # Range function only works from lower to higher. Hence reverse if prev above next.
                if prev_y >= next_y:
                    seq = reversed(range(next_y, prev_y))
                else:
                    seq = range(next_y, prev_y)
                for y in seq:
                    self.path_space[(prev_x, y)].append((prev_x, y+1))


    def path_check(self, path_sketch):
        print(path_sketch)
        for i in range(1, len(path_sketch)):
            prev_x, prev_y = path_sketch[i-1]
            next_x, next_y = path_sketch[i]
            if next_x != prev_x:
                for x in range(prev_x, next_x):
                    pass
            else:
                for y in range(prev_y, next_y):
                    pass

        return True