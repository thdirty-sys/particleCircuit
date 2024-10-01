import numpy as np


class Node:
    def __init__(self, start_pos, rate):
        self.name = "node"
        self.pos = start_pos
        self.rate = rate
        self.count = 0
        self.check_in = []

    def take(self, t):
        if len(self.check_in) == 10:
            self.check_in.pop(0)
        self.check_in.append(t)


class Particle:
    """General element of the Circuit"""

    def __init__(self, start_pos, number):
        self.pos = start_pos
        self.name = "particle"
        self.orientation = "-"
        self.no = number


class Repository:
    """Repository object; fed particles."""

    def __init__(self, start_pos, capacity):
        self.name = "repo"
        self.capacity = capacity
        self.pos = start_pos
        self.count = 0
        self.check_in = []

    def in_column_entry_space(self, x):
        if self.pos[0] == x:
            return True
        else:
            return False

    def take(self, t):
        if len(self.check_in) == 10:
            self.check_in.pop(0)
        self.check_in.append(t)




class Circuit:
    """The circuit, with all its received features. Must have/generate paths to be functional.
    Given entry/exit nodes necessary, as well as repositories."""

    def __init__(self, repos, ingress, egress):
        self.repos = repos
        self.entry_nodes = ingress
        self.exit_nodes = egress
        self.body = self.repos + self.exit_nodes
        self.path_setup()

    def path_setup(self):
        self.current_obj = "-"
        self.path_orientation = {}
        self.path_space = {}
        self.splits = {}
        self.wipe_paths()

        self.particles = []
        self.undercurrent_space = {}

    def wipe_paths(self):
        for y in range(26):
            for x in range(50):
                self.path_space[(x, y)] = []
                self.path_orientation[(x, y)] = "-"

    def gen_circuit_paths(self):
        rng = np.random.default_rng()

        # First settings for main entry node path
        available = self.repos[1:]
        next_connections = self.repos

        # Count to keep track of index of available nodes for branching
        attempts = 1

        pointer_pos = self.entry_nodes[0].pos

        # Generate a path for a node, and begin recursive branch process from that path
        for node in self.entry_nodes + self.repos:
            pointer_pos = node.pos
            for connection in next_connections:
                path = self.path_find(pointer_pos, connection.pos)
                if path:
                    break
            self.branch_path_construct(pointer_pos, 1, prev=self.path_orientation[connection.pos])

            # Make sure we have the right selection of nodes for branches
            if attempts >= len(self.repos):
                available = self.exit_nodes
            else:
                available = self.body[attempts:]
                attempts += 1

            # Randomly selected sequence of nodes to connect next too
            next_connections = rng.choice(available, len(available), replace=False)

        # For any repo without a path to it, generate that path
        # Switch up order of repos first however
        mixed = rng.choice(self.repos, len(self.repos), replace=False)
        for repo in mixed:
            current_ind = self.repos.index(repo)
            possible_connections = self.entry_nodes + self.repos[:current_ind]
            connection_queue = rng.choice(possible_connections, len(possible_connections), replace=False)
            for node in connection_queue:
                path = self.path_find(node.pos, repo.pos)
                if path:
                    break

        # Make sure our splits dictionary is up-to-date with splits at repos/entry nodes
        for node in self.entry_nodes + self.repos:
            self.splits[node.pos] = self.path_space[node.pos]

        # Clean out unnecessary routing covered by undercurrent dictionary
        '''for pos in self.path_space:
            for p in self.path_space[pos]:
                if self.path_orientation[p] != self.path_orientation[pos]:
                    if not self.in_repo(p) and not self.in_exit_node(p):
                        if pos in self.splits:
                            if p not in self.splits[pos]:
                                if p not in self.undercurrent_space[self.path_orientation[pos]]:
                                    self.path_space[pos].remove(p)
                        else:
                            if p not in self.undercurrent_space[self.path_orientation[pos]]:
                                self.path_space[pos].remove(p)'''
        self.path_orientation[self.entry_nodes[0].pos] = "-"

        for repo in self.repos:
            if not self.pos_is_pointed_towards(repo.pos) or not self.path_space[repo.pos]:
                self.path_setup()
                return False
        else:
            return True

    def branch_path_construct(self, pointer, p, prev="-"):
        """Recursively called to generate path space"""

        rng = np.random.default_rng()
        pointer_pos = pointer

        # Only consider repos and exit nodes with a higher x value than pointer, since whole process is left to right
        for i, repo in enumerate(self.repos):
            if pointer_pos[0] < repo.pos[0]:
                available = self.repos[i:] + self.exit_nodes
                break
        else:
            available = self.exit_nodes

        # Make random selection from available
        no_available = len(available)
        no_selected = rng.binomial(no_available, min(p / no_available, 1))
        selected = rng.choice(available, no_selected, replace=False)

        for node in selected:
            node_orientation = str(node.pos)
            pointer_orientation = self.path_orientation[pointer_pos]
            if node_orientation != self.path_orientation[pointer_pos]:
                # Select the second block along in current branch after the pointer_pos
                for pos in self.path_space[pointer_pos]:
                    if self.path_orientation[pos] == pointer_orientation:
                        pointer_pos = pos
                        break
                for pos in self.path_space[pointer_pos]:
                    if self.path_orientation[pos] == pointer_orientation:
                        pointer_pos = pos
                        break
                # Test if we are still along the branch path
                if self.in_repo(pointer_pos) or node_orientation == prev:
                    break
                # If so generate new path and call recursion
                else:
                    path = self.path_find(pointer_pos, node.pos)
                    if path:
                        for pos in self.path_space[pointer_pos]:
                            # Select path newly created
                            if self.path_orientation[pos] == node_orientation:
                                # Extra condition for fixing undercurrent bug
                                if pos not in self.undercurrent_space:
                                    if pointer_pos in self.splits:
                                        self.splits[pointer_pos].append(pos)
                                    else:
                                        self.splits[pointer_pos] = [pos]
                                    self.branch_path_construct(pos, p / 2, prev=pointer_orientation)
                                    break



    def pos_is_pointed_towards(self, pos):
        x, y = pos
        set = self.path_space
        if (x, y) in self.path_space:
            collected_array = set[((x + 1) % 50, y)] + set[(x - 1, y)] + set[(x, y + 1)] + set[(x, y - 1)]
        else:
            return False
        return (pos in collected_array)

    def in_repo(self, pos):
        for node in self.repos:
            if pos == node.pos:
                return True
        else:
            return False

    def in_exit_node(self, pos):
        for node in self.exit_nodes:
            if pos == node.pos:
                return True
        else:
            return False

    def in_entry_node(self, pos):
        for node in self.entry_nodes:
            if pos == node.pos:
                return True
        else:
            return False

    def in_node(self, pos):
        return self.in_entry_node(pos) or self.in_exit_node(pos)

    def path_find(self, start, target, hovering=False):
        target_x, target_y = target
        start_x, start_y = start
        found = False

        if self.in_repo(target) or self.in_node(target):
            self.current_obj = str(target)
        else:
            self.current_obj = self.path_orientation[target]


        # Construct path
        for elbow_room in range(0, max(26 - start_y, start_y + 1), 2):
            if start_y - elbow_room < 0:
                pass
            else:
                pos_sketch_lower = [start, (start_x, start_y - elbow_room), (target_x, start_y - elbow_room),
                                    target]
                if self.path_check(pos_sketch_lower):
                    if not hovering:
                        self.gen_path(pos_sketch_lower)
                    found = True
                    break

            if start_y + elbow_room > 25:
                pass
            else:
                pos_sketch_higher = [start, (start_x, start_y + elbow_room), (target_x, start_y + elbow_room),
                                     target]
                if self.path_check(pos_sketch_higher):
                    if not hovering:
                        self.gen_path(pos_sketch_higher)
                    found = True
                    break

        # If not found, try again but by steps of 1
        if not found:
            for elbow_room in range(0, max(26 - start_y, start_y + 1), 2):
                if start_y - elbow_room < 0:
                    pass
                else:
                    pos_sketch_lower = [start, (start_x, start_y - elbow_room), (target_x, start_y - elbow_room),
                                        target]
                    if self.path_check(pos_sketch_lower):
                        if not hovering:
                            self.gen_path(pos_sketch_lower)
                        found = True
                        break

                if start_y + elbow_room > 25:
                    pass
                else:
                    pos_sketch_higher = [start, (start_x, start_y + elbow_room), (target_x, start_y + elbow_room),
                                         target]
                    if self.path_check(pos_sketch_higher):
                        if not hovering:
                            self.gen_path(pos_sketch_higher)
                        found = True
                        break
        return found

    def gen_path(self, path_sketch):

        # Draws paths between each corner and adds it to path space
        for i in range(1, len(path_sketch)):
            prev_x, prev_y = path_sketch[i - 1]
            next_x, next_y = path_sketch[i]
            if next_x != prev_x:
                for x in range(prev_x, next_x):
                    if self.path_orientation[(x, prev_y)] != self.current_obj:
                        if self.path_orientation[(x, prev_y)] != "-":
                            if x == prev_x and (prev_x, prev_y) == path_sketch[0]:
                                self.path_space[(x, prev_y)].append((x + 1, prev_y))
                            else:
                                self.undercurrent_space[(x, prev_y)] = (x + 1, prev_y)
                        else:
                            self.path_orientation[(x, prev_y)] = self.current_obj
                            self.path_space[(x, prev_y)].append((x + 1, prev_y))

            else:
                # Range function only works from lower to higher. Hence reverse if prev above next.
                if prev_y >= next_y:
                    for y in reversed(range(next_y + 1, prev_y + 1)):
                        if self.path_orientation[(prev_x, y)] != self.current_obj:
                            if self.path_orientation[(prev_x, y)] != "-":
                                if y == prev_y and (prev_x, prev_y) == path_sketch[0]:
                                    self.path_space[(prev_x, y)].append((prev_x, y - 1))
                                else:
                                    self.undercurrent_space[(prev_x, y)] = (prev_x, y - 1)
                            else:
                                self.path_orientation[(prev_x, y)] = self.current_obj
                                self.path_space[(prev_x, y)].append((prev_x, y - 1))

                else:
                    for y in range(prev_y, next_y):
                        if self.path_orientation[(prev_x, y)] != self.current_obj:
                            if self.path_orientation[(prev_x, y)] != "-":
                                if y == prev_y and (prev_x, prev_y) == path_sketch[0]:
                                    self.path_space[(prev_x, y)].append((prev_x, y + 1))
                                else:
                                    self.undercurrent_space[(prev_x, y)] = (prev_x, y + 1)
                            else:
                                self.path_orientation[(prev_x, y)] = self.current_obj
                                self.path_space[(prev_x, y)].append((prev_x, y + 1))

    def path_check(self, path_sketch):
        for i in range(1, len(path_sketch)):
            prev_x, prev_y = path_sketch[i - 1]
            next_x, next_y = path_sketch[i]
            if next_x != prev_x:
                for x in range(prev_x, next_x):
                    orientation = self.path_orientation[(x, prev_y)]
                    # Laterally, check there are no crossing paths heading in the same direction
                    if orientation != self.current_obj and orientation != "-":
                        if self.path_orientation[(x + 1, prev_y)] == self.current_obj:
                            return False
                        if not self.is_crossable_x(x, prev_y):
                            return False
                        if (x, prev_y) == (prev_x + 1, prev_y):
                            return False
                    elif orientation == self.current_obj:
                        if (x + 1, prev_y) not in self.path_space[(x, prev_y)]:
                            return False
                    if self.in_repo((x, prev_y)) and (x, prev_y) != path_sketch[0]:
                        return False
            else:
                # Range function only works from lower to higher. Hence reverse if prev above next.
                if prev_y >= next_y:
                    for y in reversed(range(next_y + 1, prev_y + 1)):
                        orientation = self.path_orientation[(prev_x, y)]
                        if orientation != "-" and orientation != self.current_obj:
                            if self.path_orientation[(prev_x, y - 1)] == self.current_obj:
                                return False
                            if not self.is_crossable_y(prev_x, y):
                                return False
                            if (prev_x, prev_y) == (prev_x, prev_y - 1):
                                return False
                        elif orientation == self.current_obj:
                            if (prev_x, y - 1) not in self.path_space[(prev_x, y)]:
                                return False
                else:
                    for y in range(prev_y, next_y):
                        orientation = self.path_orientation[(prev_x, y)]
                        if orientation != "-" and orientation != self.current_obj:
                            if self.path_orientation[(prev_x, y + 1)] == self.current_obj:
                                return False
                            if not self.is_crossable_y(prev_x, y, down=False):
                                return False
                            if (prev_x, prev_y) == (prev_x, prev_y + 1):
                                return False
                        elif orientation == self.current_obj:
                            if (prev_x, y + 1) not in self.path_space[(prev_x, y)]:
                                return False
        return True

    def is_crossable_x(self, x, prev_y):
        traversable = (x + 1, prev_y) not in self.path_space[(x, prev_y)]
        continuable = self.path_orientation[(x + 1, prev_y)] == "-"

        return traversable and continuable

    def is_crossable_y(self, prev_x, y, down=True):
        if down:
            traversable = (prev_x, y - 1) not in self.path_space[(prev_x, y)]
            continuable = self.path_orientation[(prev_x, y - 1)] == "-"
        else:
            traversable = (prev_x, y + 1) not in self.path_space[(prev_x, y)]
            continuable = self.path_orientation[(prev_x, y + 1)] == "-"

        return traversable and continuable

    def complete(self):
        if len(self.particles) < 200:
            return False
        else:
            return True
