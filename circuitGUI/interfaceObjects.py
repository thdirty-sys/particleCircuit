import dearpygui.dearpygui as dpg

class CircuitImage():
    def __init__(self, circuit):
        self.path_rec_count = 0
        self.sep_line_count = 0
        self.c = circuit

    def show_nodes(self):
        circuit = self.c

        for i, repo in enumerate(circuit.repos):
            dpg.draw_rectangle(pmin=repo.pos, pmax=repo.pos, parent="main_grid",
                               color=(233, 12, 50), tag=f"repo{i}")
            dpg.draw_text(repo.pos, 0, parent="main_grid", tag="repo_text" + str(i), size=0.5, color=(0, 250, 250))

        for i, en_node in enumerate(circuit.entry_nodes):
            dpg.draw_rectangle(pmin=en_node.pos, pmax=en_node.pos, parent="main_grid",
                               color=(233, 240, 50), tag="entry_node" + str(i))
            dpg.draw_text((en_node.pos[0] - 0.5, en_node.pos[1] + 0.5), round(en_node.rate, 3), parent="main_grid",
                          tag="en_node_text" + str(i), size=0.35, color=(0, 0, 0))

        for i, ex_node in enumerate(circuit.exit_nodes):
            dpg.draw_rectangle(pmin=ex_node.pos, pmax=ex_node.pos, parent="main_grid",
                               color=(23, 240, 250), tag="exit_node" + str(i))
            dpg.draw_text((ex_node.pos[0] - 0.5, ex_node.pos[1] + 0.5), round(-ex_node.rate, 3), parent="main_grid",
                          tag="ex_node_text" + str(i), size=0.35, color=(0, 1, 0))

    def show_paths(self):
        circuit = self.c
        path_space = circuit.path_space
        for pos in path_space:
            if path_space[pos] != [] and (not circuit.in_repo(pos)) and (not circuit.in_node(pos)):
                # Set colour grading for different node orientations
                l = len(circuit.repos + circuit.exit_nodes)
                for i, n in enumerate(circuit.repos + circuit.exit_nodes):
                    if circuit.path_orientation[pos] == str(n.pos):
                        break
                col = ((i+1)*255/l, 50, 100)

                # Draw rectangle
                dpg.draw_rectangle(pmin=pos, pmax=pos, parent="main_grid", color=col,
                                   tag="path_block" + str(self.path_rec_count), before="repo_text0")
                self.path_rec_count += 1

                adjacent = self.valid_adjacents(pos)
                for a in adjacent:
                    if not circuit.in_repo(a) and not circuit.in_node(a):
                        if a not in path_space[pos] and pos not in path_space[a]:
                            self.draw_sep_line(pos, a)
                            self.sep_line_count += 1
                        else:
                            if circuit.path_orientation[pos] != circuit.path_orientation[a]:
                                if pos in circuit.splits:
                                    if a not in circuit.splits[pos]:
                                        self.draw_sep_line(pos, a)
                                        self.sep_line_count += 1
                                elif a in circuit.splits:
                                    if pos not in circuit.splits[a]:
                                        self.draw_sep_line(pos, a)
                                        self.sep_line_count += 1
                                else:
                                    self.draw_sep_line(pos, a)
                                    self.sep_line_count += 1
                    # Fix case where undercurrent path feeds into repo but no line drawn
                    elif a in path_space[pos]:
                        if circuit.path_orientation[pos] != str(a):
                            print("again")
                            self.draw_sep_line(pos, a)
                            self.sep_line_count += 1

        # Deal with sep lines for nodes
        for node in circuit.entry_nodes + circuit.body:
            adjacent = self.valid_adjacents(node.pos)
            for a in adjacent:
                if node.pos not in path_space[a] and a not in path_space[node.pos]:
                    self.draw_sep_line(node.pos, a)
                    self.sep_line_count += 1

    def draw_sep_line(self, w, v):
        w_x, w_y = w
        v_x, v_y = v

        if w_x - v_x == 0:
            line_y = min(v_y, w_y) + 0.5
            dpg.draw_line((v_x - 0.55, line_y), (v_x + 0.55, line_y), color=(0, 0, 0, 255), parent="main_grid",
                          tag="sep_line" + str(self.sep_line_count), thickness=0.08)
        else:
            line_x = min(v_x, w_x) + 0.5
            dpg.draw_line((line_x, v_y - 0.55), (line_x, v_y + 0.55), color=(0, 0, 0, 255), parent="main_grid",
                          tag="sep_line" + str(self.sep_line_count), thickness=0.08)

    def valid_adjacents(self, pos):
        """Given a position value, return adjacent positions which are in the valid range"""
        x, y = pos
        adjacent_pos = [(x + 1, y), (x, y - 1), (x, y + 1), (x - 1, y)]
        valid = []
        for p in adjacent_pos:
            a, b = p
            if -1 < a < 50 and -1 < b < 26:
                valid.append(p)
        return valid

    def hide_paths(self):
        for i in range(self.path_rec_count):
            dpg.delete_item("path_block" + str(i))

        for i in range(self.sep_line_count):
            dpg.delete_item("sep_line" + str(i))

    def hide_nodes(self):
        circuit = self.c

        for i in range(len(circuit.repos)):
            dpg.delete_item("repo" + str(i))
            dpg.delete_item("repo_text" + str(i))

        for i in range(len(circuit.entry_nodes)):
            dpg.delete_item("entry_node" + str(i))
            dpg.delete_item("en_node_text" + str(i))

        for i in range(len(circuit.exit_nodes)):
            dpg.delete_item("exit_node" + str(i))
            dpg.delete_item("ex_node_text" + str(i))


