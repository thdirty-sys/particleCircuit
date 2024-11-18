import numpy as np
from copy import deepcopy
from math import floor


class Node:
    def __init__(self, start_pos, rate, **kwargs):
        self.last_t_mult = 0
        self.name = "node"
        self.pos = start_pos
        self.rate = rate
        self.count = 0
        self.check_in = [0]
        self.track = True
        for key in kwargs:
            self.__dict__[key] = kwargs[key]

    def take(self, t):
        if self.track:
            self.check_in.append(t)



class Particle:

    def __init__(self, start_pos, number):
        self.pos = start_pos
        self.name = "particle"
        self.orientation = None
        self.no = number


class Repository:
    """Repository object; fed particles."""

    def __init__(self, start_pos, capacity, colour=(233, 12, 50), **kwargs):
        self.last_t_mult = 0
        self.name = "repo"
        self.capacity = capacity
        self.pos = start_pos
        self.count = 0
        self.check_in = [0]
        self.colour = colour
        self.track = True
        for key in kwargs:
            self.__dict__[key] = kwargs[key]

    def in_column_entry_space(self, x):
        if self.pos[0] == x:
            return True
        else:
            return False

    def take(self, t):
        if self.track:
            self.check_in.append(t)



class Circuit:
    """The circuit, with all its received features. Must have/generate paths to be functional.
    Given entry/exit nodes necessary, as well as repositories."""

    def __init__(self, repos, ingress, egress):
        self.repos = repos
        self.entry_nodes = ingress
        self.exit_nodes = egress
        self.body = self.repos + self.exit_nodes
        self.current_obj = None
        self.path_orientation = {}
        self.path_space = {}
        self.particles = []
        self.undercurrent_space = {}
        self.undercurrent_orientation = {}
        self.reset_paths()

    def reset_paths(self):
        for y in range(26):
            for x in range(50):
                self.path_space[(x, y)] = []
                self.path_orientation[(x, y)] = None

    def add_node(self, node):
        if node.rate >= 0:
            self.entry_nodes.append(node)
        else:
            self.exit_nodes.append(node)
            self.body = self.repos + self.exit_nodes

    def add_repo(self, repo):
        self.repos.append(repo)
        self.body = self.repos + self.exit_nodes

    def delete_node(self, node):
        if node.rate >= 0:
            self.entry_nodes.remove(node)
        else:
            self.exit_nodes.remove(node)
            self.body = self.repos + self.exit_nodes

    def delete_repo(self, repo):
        self.repos.remove(repo)
        self.body = self.repos + self.exit_nodes



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

        for repo in self.repos:
            if not self.pos_is_pointed_towards(repo.pos) or not self.path_space[repo.pos]:
                self.path_setup()
                return False
        else:
            return True

    def branch_path_construct(self, pointer, p, prev=None):
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
            node_orientation = node.pos
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
                        if self.path_orientation[(x, prev_y)] != None:
                            if x == prev_x and (prev_x, prev_y) == path_sketch[0]:
                                self.path_space[(x, prev_y)].append((x + 1, prev_y))
                            else:
                                self.undercurrent_space[(x, prev_y)] = (x + 1, prev_y)
                                self.undercurrent_orientation[(x, prev_y)] = self.current_obj
                        else:
                            self.path_orientation[(x, prev_y)] = self.current_obj
                            self.path_space[(x, prev_y)].append((x + 1, prev_y))

            else:
                # Range function only works from lower to higher. Hence reverse if prev above next.
                if prev_y >= next_y:
                    for y in reversed(range(next_y + 1, prev_y + 1)):
                        if self.path_orientation[(prev_x, y)] != self.current_obj:
                            if self.path_orientation[(prev_x, y)] != None:
                                if y == prev_y and (prev_x, prev_y) == path_sketch[0]:
                                    self.path_space[(prev_x, y)].append((prev_x, y - 1))
                                else:
                                    self.undercurrent_space[(prev_x, y)] = (prev_x, y - 1)
                                    self.undercurrent_orientation[(prev_x, y)] = self.current_obj
                            else:
                                self.path_orientation[(prev_x, y)] = self.current_obj
                                self.path_space[(prev_x, y)].append((prev_x, y - 1))

                else:
                    for y in range(prev_y, next_y):
                        if self.path_orientation[(prev_x, y)] != self.current_obj:
                            if self.path_orientation[(prev_x, y)] != None:
                                if y == prev_y and (prev_x, prev_y) == path_sketch[0]:
                                    self.path_space[(prev_x, y)].append((prev_x, y + 1))
                                else:
                                    self.undercurrent_space[(prev_x, y)] = (prev_x, y + 1)
                                    self.undercurrent_orientation[(prev_x, y)] = self.current_obj
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
                    if orientation != self.current_obj and orientation != None:
                        if self.path_orientation[(x + 1, prev_y)] == self.current_obj:
                            return False
                        if not self.is_crossable_x(x, prev_y):
                            return False
                        if (x, prev_y) == (prev_x + 1, prev_y):
                            return False
                    elif orientation == self.current_obj:
                        if (x + 1, prev_y) not in self.path_space[(x, prev_y)]:
                            return False
                    if (x, prev_y) != path_sketch[0]:
                        if self.in_repo((x, prev_y)) or self.in_node((x, prev_y)):
                            return False
            else:
                # Range function only works from lower to higher. Hence reverse if prev above next.
                if prev_y >= next_y:
                    for y in reversed(range(next_y + 1, prev_y + 1)):
                        orientation = self.path_orientation[(prev_x, y)]
                        if orientation != None and orientation != self.current_obj:
                            if self.path_orientation[(prev_x, y - 1)] == self.current_obj:
                                return False
                            if not self.is_crossable_y(prev_x, y):
                                return False
                            if (prev_x, prev_y) == (prev_x, prev_y - 1):
                                return False
                        elif orientation == self.current_obj:
                            if (prev_x, y - 1) not in self.path_space[(prev_x, y)]:
                                return False
                        if (prev_x, y) != path_sketch[0]:
                            if self.in_repo((prev_x, y)) or self.in_node((prev_x, y)):
                                return False
                else:
                    for y in range(prev_y, next_y):
                        orientation = self.path_orientation[(prev_x, y)]
                        if orientation != None and orientation != self.current_obj:
                            if self.path_orientation[(prev_x, y + 1)] == self.current_obj:
                                return False
                            if not self.is_crossable_y(prev_x, y, down=False):
                                return False
                            if (prev_x, prev_y) == (prev_x, prev_y + 1):
                                return False
                        elif orientation == self.current_obj:
                            if (prev_x, y + 1) not in self.path_space[(prev_x, y)]:
                                return False
                        if (prev_x, y) != path_sketch[0]:
                            if self.in_repo((prev_x, y)) or self.in_node((prev_x, y)):
                                return False
        return True

    def is_crossable_x(self, x, prev_y):
        traversable = (x + 1, prev_y) not in self.path_space[(x, prev_y)]
        continuable = self.path_orientation[(x + 1, prev_y)] == None

        return traversable and continuable

    def is_crossable_y(self, prev_x, y, down=True):
        if down:
            traversable = (prev_x, y - 1) not in self.path_space[(prev_x, y)]
            continuable = self.path_orientation[(prev_x, y - 1)] == None
        else:
            traversable = (prev_x, y + 1) not in self.path_space[(prev_x, y)]
            continuable = self.path_orientation[(prev_x, y + 1)] == None

        return traversable and continuable

class UndoRedoCaretaker:
    def __init__(self, circuit):
        self.undo_stack = []
        self.redo_stack = []
        self._circuit = circuit

    def undo(self):
        if self.undo_stack:
            command = self.undo_stack.pop()
            inverse_command = command.execute(self._circuit)
            self.redo_stack.append(inverse_command)
            if len(self.redo_stack) == 10:
                del self.redo_stack[0]

    def redo(self):
        if self.redo_stack:
            state = self.redo_stack.pop()
            inverse_command = state.execute(self._circuit)
            self.undo_push(inverse_command)

    def undo_push(self, inverse_command):
        self.undo_stack.append(inverse_command)
        if len(self.undo_stack) == 20:
            del self.undo_stack[0]

    def new_undo_push(self, inverse_command):
        self.redo_stack = []
        self.undo_push(inverse_command)


class RestoreNodeCommand:
    def __init__(self, node):
        self.__dict__ = deepcopy(node.__dict__)

    def execute(self, circuit):
        # Finds relevant node and reverts attributes back to saved values
        for i, n in enumerate(circuit.body + circuit.entry_nodes):
            if self.pos == n.pos:
                # Saves inverse of command
                inverse_command = RestoreNodeCommand(n)
                # Updates relevant node
                n.__dict__ = deepcopy(self.__dict__)
                break

        # Returns inverse for undo/redo stack
        return inverse_command


class DeleteNodeCommand:
    def __init__(self, node):
        self.pos = node.pos
        self.name = node.name

    def execute(self, circuit):
        # Deletes repo if node
        if self.name == "repo":
            for i, r in enumerate(circuit.repos):
                if self.pos == r.pos:
                    inverse_command = CreateNodeCommand(r)
                    del circuit.repos[i]
                    break
        else:
            # Deletes entry node
            for i, en in enumerate(circuit.entry_nodes):
                if self.pos == en.pos:
                    inverse_command = CreateNodeCommand(en)
                    del circuit.entry_nodes[i]
                    break
            else:
                # Deletes exit node
                for i, ex in enumerate(circuit.exit_nodes):
                    if self.pos == ex.pos:
                        inverse_command = CreateNodeCommand(ex)
                        del circuit.exit_nodes[i]
                        break
        return inverse_command


class CreateNodeCommand:
    def __init__(self, node):
        self.__dict__ = deepcopy(node.__dict__)

    def execute(self, circuit):
        # Creates node and returns inverse command for redo/undo stack
        if self.name == 'repo':
            del self.__dict__['capacity']
            repo = Repository(self.pos, 100, **self.__dict__)
            inverse_command = DeleteNodeCommand(repo)
            circuit.add_repo(repo)
            return inverse_command
        else:
            node = Node(self.pos, self.rate)
            inverse_command = DeleteNodeCommand(node)
            circuit.add_node(node)
            return inverse_command

class PathsRestoreCommand:
    def __init__(self, circuit):
        self.memento = {}
        for y in range(26):
            for x in range(50):
                if circuit.path_orientation[(x, y)] != None:
                    self.memento[(x, y)] = [circuit.path_space[(x, y)].copy(), circuit.path_orientation[(x, y)]]
                    if (x, y) in circuit.undercurrent_space:
                        self.memento[(x, y)].append(circuit.undercurrent_space[(x, y)])
                        self.memento[(x, y)].append(circuit.undercurrent_orientation[(x, y)])
                    else:
                        self.memento[(x, y)].append(None)
                        self.memento[(x, y)].append(None)

    def execute(self, circuit):
        inverse_command = PathsRestoreCommand(circuit)
        for y in range(26):
            for x in range(50):
                if (x, y) in self.memento:
                    circuit.path_space[(x, y)] = self.memento[(x, y)][0]
                    circuit.path_orientation[(x, y)] = self.memento[(x, y)][1]
                    if self.memento[(x, y)][2] is not None:
                        circuit.undercurrent_space[(x, y)] = self.memento[(x, y)][2]
                        circuit.undercurrent_orientation[(x, y)] = self.memento[(x, y)][3]
                else:
                    circuit.path_space[(x, y)] = []
                    circuit.path_orientation[(x, y)] = None
                    circuit.undercurrent_space[(x, y)] = []
                    circuit.undercurrent_orientation[(x, y)] = None
        return inverse_command

class RandomCompleteCircuitGenerator:
    def __init__(self):
        self.circuit = None
    def gen_circuit(self):
        """Generate circuit (without any paths)."""
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

    def gen_circuit_paths(self):
        """Generates paths"""
        rng = np.random.default_rng()
        c = self.circuit

        # First settings for main entry node path
        next_connections = c.repos

        # Count to keep track of index of available nodes for branching
        attempts = 1

        # Generate a path for a node, and begin recursive branch process from that path
        for node in c.entry_nodes + c.repos:
            pointer_pos = node.pos
            for connection in next_connections:
                path = c.path_find(pointer_pos, connection.pos)
                if path:
                    break
            self.branch_path_construct(pointer_pos, 1, prev=c.path_orientation[connection.pos])

            # Make sure we have the right selection of nodes for branches
            if attempts >= len(c.repos):
                available = c.exit_nodes
            else:
                available = c.body[attempts:]
                attempts += 1

            # Randomly selected sequence of nodes to connect next too
            next_connections = rng.choice(available, len(available), replace=False)

        # For any repo without a path to it, generate that path
        # Switch up order of repos first however
        mixed = rng.choice(c.repos, len(c.repos), replace=False)
        for repo in mixed:
            current_ind = c.repos.index(repo)
            possible_connections = c.entry_nodes + c.repos[:current_ind]
            connection_queue = rng.choice(possible_connections, len(possible_connections), replace=False)
            for node in connection_queue:
                path = c.path_find(node.pos, repo.pos)
                if path:
                    break

        for repo in c.repos:
            if not c.pos_is_pointed_towards(repo.pos) or not c.path_space[repo.pos]:
                self.path_setup()
                return False
        else:
            return True

    def branch_path_construct(self, pointer, p, prev=None):
        """Recursively called to generate path space"""
        rng = np.random.default_rng()
        pointer_pos = pointer
        c = self.circuit

        # Only consider repos and exit nodes with a higher x value than pointer, since whole process is left to right
        for i, repo in enumerate(c.repos):
            if pointer_pos[0] < repo.pos[0]:
                available = c.repos[i:] + c.exit_nodes
                break
        else:
            available = c.exit_nodes

        # Make random selection from available
        no_available = len(available)
        no_selected = rng.binomial(no_available, min(p / no_available, 1))
        selected = rng.choice(available, no_selected, replace=False)

        for node in selected:
            node_orientation = node.pos
            pointer_orientation = c.path_orientation[pointer_pos]
            if node_orientation != c.path_orientation[pointer_pos]:
                # Select the second block along in current branch after the pointer_pos
                for pos in c.path_space[pointer_pos]:
                    if c.path_orientation[pos] == pointer_orientation:
                        pointer_pos = pos
                        break
                for pos in c.path_space[pointer_pos]:
                    if c.path_orientation[pos] == pointer_orientation:
                        pointer_pos = pos
                        break
                # Test if we are still along the branch path
                if c.in_repo(pointer_pos) or node_orientation == prev:
                    break
                # If so generate new path and call recursion
                else:
                    path = c.path_find(pointer_pos, node.pos)
                    if path:
                        for pos in c.path_space[pointer_pos]:
                            # Select path newly created
                            if c.path_orientation[pos] == node_orientation:
                                # Extra condition for fixing undercurrent bug
                                if pos not in c.undercurrent_space:
                                    self.branch_path_construct(pos, p / 2, prev=pointer_orientation)
                                    break

    def path_setup(self):
        self.circuit.current_obj = None
        self.circuit.path_orientation = {}
        self.circuit.path_space = {}
        self.circuit.particles = []
        self.circuit.undercurrent_space = {}
        self.circuit.undercurrent_orientation = {}
        self.circuit.reset_paths()

class DataRecorder:
    def __init__(self, tracked_nodes):
        self.nodes = tracked_nodes
        self.currents_1 = {}
        self.currents_10 = {}
        self.currents_50 = {}

        for node in self.nodes:
            self.currents_1[node.pos] = [0]
            self.currents_10[node.pos] = []
            self.currents_50[node.pos] = []

    def calc_currents(self):
        for pos in self.currents_1:
            for i in range(len(self.currents_1[pos]) // 10):
                self.currents_10[pos].append(sum(self.currents_1[pos][i * 10:i * 10 + 10]) / 10)
            for i in range(len(self.currents_1[pos]) // 50):
                self.currents_50[pos].append(sum(self.currents_1[pos][i * 50:i * 50 + 50]) / 50)
            self.currents_1[pos] = [0]