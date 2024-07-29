import numpy as np
class Node:
    def __init__(self, start_pos, rate):
        self.name = "node"
        self.pos = start_pos
        self.rate = rate


class Particle:
    """General element of the Circuit"""
    def __init__(self, start_pos):
        self.pos = start_pos
        self.name = "particle"


class Repository:
    """Repository object; fed particles."""
    def __init__(self, start_pos, capacity):
        self.name = "repo"
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
        self.branches = 0
        self.repos = repos
        self.entry_nodes = ingress
        self.exit_nodes = egress
        self.current_obj = "-"

        self.path_orientation = {}
        self.path_space = {}
        for y in range(26):
            for x in range(50):
                self.path_space[(x,y)] = []
                self.path_orientation[(x,y)] = "-"

        self.particles = []

    def gen_circuit_paths(self):
        rng = np.random.default_rng()

        # Generate first, necessary path
        self.current_obj = "0"
        self.path_find(self.entry_nodes[0].pos, self.repos[0].pos)

        # Select number of nodes to be attached to first branch binomially
        available = self.repos[1:]
        no_available = len(available)
        no_selected = rng.binomial(no_available, 1/2)
        selected = rng.choice(available, no_selected, replace=False)

        # First branch
        pointer_pos = self.entry_nodes[0].pos
        for repo in selected:
            # Select the second block along in current branch after the pointer_pos. It has to be valid though.
            if self.path_space[pointer_pos] != []:
                pointer_pos = self.path_space[pointer_pos][0]
                if self.path_space[pointer_pos] != []:
                    pointer_pos = self.path_space[pointer_pos][0]
            # Check it is not a repo position, or invalid position.
            if self.in_repo_or_exit(pointer_pos) or pointer_pos == []:
                break
            else:
                self.current_obj = str(self.repos.index(repo))
                self.path_find(pointer_pos, repo.pos)
                print(pointer_pos, self.path_space[pointer_pos])
                # Begin recursive branch out path generation
                self.branch_path_construct(self.path_space[pointer_pos][0], 1/2)



    def in_repo_or_exit(self, pos):
        for repo in self.repos:
            if pos == repo.pos:
                return True

        for node in self.exit_nodes:
            if node.pos == pos:
                return True

    def branch_path_construct(self, pointer, p):
        """Recursively called to generate path space"""

        self.branches += 1
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
        print(available)
        no_available = len(available)
        no_selected = rng.binomial(no_available, p)
        selected = rng.choice(available, no_selected, replace=False)

        for node in selected:
            # Select the second block along in current branch after the pointer_pos
            if self.path_space[pointer_pos] != []:
                pointer_pos = self.path_space[pointer_pos][0]
                if self.path_space[pointer_pos] != []:
                    pointer_pos = self.path_space[pointer_pos][0]
            # Test if we are still along the branch path
            if self.in_repo_or_exit(pointer_pos) or pointer_pos == []:
                break
            # If so generate new path and call recursion
            else:
                if node.name == "repo":
                    self.current_obj = str(self.repos.index(node))
                else:
                    self.current_obj = "a"+str(self.exit_nodes.index(node))
                self.path_find(pointer_pos, node.pos)
                # Begin recursive branch-out path generation
                self.branch_path_construct(self.path_space[pointer_pos][0], p*2/3)





    def path_find(self, start, target):
        target_x, target_y = target
        start_x, start_y = start
        found = False

        # Construct path
        l_supplement = 0
        u_supplement = 0

        for elbow_room in range(0, max(26-start_y, start_y+1), 2):
            if start_y - elbow_room < 0:
                pass
            else:
                pos_sketch_lower = [start, (start_x, start_y - elbow_room), (target_x, start_y - elbow_room), target]
                if self.path_check(pos_sketch_lower):
                    self.gen_path(pos_sketch_lower)
                    found = True
                    break

            if start_y + elbow_room > 25:
                pass
            else:
                pos_sketch_higher = [start, (start_x, start_y + elbow_room), (target_x, start_y + elbow_room),
                                     target]
                if self.path_check(pos_sketch_higher):
                    self.gen_path(pos_sketch_higher)
                    found = True
                    break

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
                    for y in reversed(range(next_y+1, prev_y+1)):
                        self.path_space[(prev_x, y)].append((prev_x, y - 1))
                        if self.path_orientation[(prev_x, y)] == "-":
                            self.path_orientation[(prev_x, y)] = self.current_obj

                else:
                    for y in range(prev_y, next_y):
                        self.path_space[(prev_x, y)].append((prev_x, y+1))
                        if self.path_orientation[(prev_x, y)] == "-":
                            self.path_orientation[(prev_x, y)] = self.current_obj

    def path_check(self, path_sketch):
        for i in range(1, len(path_sketch)):
            prev_x, prev_y = path_sketch[i-1]
            next_x, next_y = path_sketch[i]
            if next_x != prev_x:
                for x in range(prev_x, next_x):
                    # Laterally, check there are no crossing paths heading in the same direction
                    if (x+1, prev_y) in self.path_space[(x, prev_y)]:
                        return False
            else:
                # Range function only works from lower to higher. Hence reverse if prev above next.
                if prev_y >= next_y:
                    for y in reversed(range(next_y + 1, prev_y + 1)):
                        self.path_space[(prev_x, y)].append((prev_x, y - 1))
                else:
                    for y in range(prev_y, next_y):
                        self.path_space[(prev_x, y)].append((prev_x, y + 1))

        return True