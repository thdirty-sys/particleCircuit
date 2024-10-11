import dearpygui.dearpygui as dpg
import threading
import circuitOperations.circuitDispatchers as circuitDispatchers



class RepeatTimer(threading.Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)


class Thread(threading.Thread):
    pass


class CircuitImage():
    def __init__(self, circuit):
        self.path_rec_count = 0
        self.sep_line_count = 0
        self.c = circuit

    def show_nodes(self):
        circuit = self.c

        for repo in circuit.repos:
            dpg.draw_rectangle(pmin=repo.pos, pmax=repo.pos, parent="main_grid",
                               color=repo.colour, tag=f"repo_{repo.pos}")
            dpg.draw_text(repo.pos, "0", parent="main_grid", tag=f"repo_text_{repo.pos}", size=0.5, color=(0, 250, 250))

        for i, en_node in enumerate(circuit.entry_nodes):
            dpg.draw_rectangle(pmin=en_node.pos, pmax=en_node.pos, parent="main_grid",
                               color=(233, 240, 50), tag=f"node_{en_node.pos}")
            dpg.draw_text((en_node.pos[0] - 0.5, en_node.pos[1] + 0.5), round(en_node.rate, 3), parent="main_grid",
                          tag=f"node_text_{en_node.pos}", size=0.35, color=(0, 0, 0))

        for i, ex_node in enumerate(circuit.exit_nodes):
            dpg.draw_rectangle(pmin=ex_node.pos, pmax=ex_node.pos, parent="main_grid",
                               color=(23, 240, 250), tag=f"node_{ex_node.pos}")
            dpg.draw_text((ex_node.pos[0] - 0.5, ex_node.pos[1] + 0.5), round(-ex_node.rate, 3), parent="main_grid",
                          tag=f"node_text_{ex_node.pos}", size=0.35, color=(0, 1, 0))

    def show_paths(self):
        self.path_rec_count = 0
        self.sep_line_count = 0
        circuit = self.c
        path_space = circuit.path_space
        for pos in path_space:
            if path_space[pos] != [] and (not circuit.in_repo(pos)) and (not circuit.in_node(pos)):
                # Set colour grading for different node orientations
                l = 1
                i = 0
                for i, n in enumerate(circuit.repos + circuit.exit_nodes):
                    if circuit.path_orientation[pos] == str(n.pos):
                        l = len(circuit.repos + circuit.exit_nodes)
                        break
                col = (round((i + 1) * 255 / l), 50, 100)

                # Draw rectangle
                dpg.draw_rectangle(pmin=pos, pmax=pos, parent="main_grid", color=col,
                                   tag="path_block" + str(self.path_rec_count), before="repo_text0")
                self.path_rec_count += 1

                adjacent = self.valid_adjacents(pos)
                for a in adjacent:
                    if not circuit.in_repo(a) and not circuit.in_node(a):
                        # Draw line between positions if they don't interact in any way
                        if a not in path_space[pos] and pos not in path_space[a]:
                            self.draw_sep_line(pos, a)
                            self.sep_line_count += 1
                        # Otherwise, draw line their orientations aren't the same and it isnt a branch splitting...
                        elif circuit.path_orientation[pos] != circuit.path_orientation[a]:
                            if a in path_space[pos]:
                                if a in circuit.undercurrent_space:
                                    if circuit.undercurrent_orientation[a] == circuit.path_orientation[pos]:
                                        self.draw_sep_line(pos, a)
                                        self.sep_line_count += 1

        # Deal with sep lines for nodes
        for node in circuit.entry_nodes + circuit.exit_nodes + circuit.repos:
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
            dpg.delete_item(f"path_block{i}")

        for i in range(self.sep_line_count):
            dpg.delete_item(f"sep_line{i}")

    def hide_nodes(self):
        circuit = self.c

        for repo in circuit.repos:
            dpg.delete_item(f"repo_text_{repo.pos}")
            dpg.delete_item(f"repo_{repo.pos}")

        for en in circuit.entry_nodes:
            dpg.delete_item(f"node_{en.pos}")
            dpg.delete_item(f"node_text_{en.pos}")

        for ex in circuit.exit_nodes:
            dpg.delete_item(f"node_{ex.pos}")
            dpg.delete_item(f"node_text_{ex.pos}")

        for i in range(self.sep_line_count):
            dpg.delete_item(f"sep_line{i}")


class TasepCircuitDispatcherGUI(circuitDispatchers.TasepCircuitDispatcher):
    def display_currents(self):
        for i, en in enumerate(self.circuit.entry_nodes):
            if en.count != 0:
                dpg.configure_item(f"en_node_current{en.pos}",
                                   default_value="Current: " + str(
                                       round(len(en.check_in) / (self.play_time - en.check_in[0]), 3)) + "p/s")

        for i, ex in enumerate(self.circuit.exit_nodes):
            if ex.count != 0:
                dpg.configure_item(f"ex_node_current{ex.pos}",
                                   default_value="Current: " + str(
                                       round(len(ex.check_in) / (self.play_time - ex.check_in[0]), 3)) + "p/s")

        for i, repo in enumerate(self.circuit.repos):
            if repo.count != 0:
                dpg.configure_item("repo_current" + str(i),
                                   default_value="Current: " + str(
                                       round(len(repo.check_in) / (self.play_time - repo.check_in[0]), 3)) + "p/s")

    def entry_handle(self, chosen):
        if self.particle_count % 10 == 0 and self.debug_particle:
            col = (255, 100, 0)
        else:
            col = (255, 255, 255)
        dpg.draw_circle(chosen.pos, 0.3, fill=col, parent="main_grid",
                        tag="particle" + str(self.particle_count))
        self.particle_count += 1
        chosen.count += 1
        chosen.take(self.play_time)

    def draw_control_menu(self):
        dpg.add_group(tag="stats", parent="control")
        dpg.add_spacer(height=2, parent="stats")
        dpg.add_text("Click node on grid\nto identify:", parent="stats", indent=40)
        dpg.add_spacer(height=9, parent="stats")
        for en_node in self.circuit.entry_nodes:
            dpg.add_group(tag=f"en_stat_list{en_node.pos}", parent="stats", horizontal=True)
            dpg.add_drawlist(tag=f"en_node_drawspace{en_node.pos}", parent=f"en_stat_list{en_node.pos}", width=50, height=50)
            dpg.draw_rectangle(parent=f"en_node_drawspace{en_node.pos}", pmin=(0, 0), pmax=(25, 25), fill=(233, 240, 50),
                               color=(0, 0, 0), tag=f"menu_rec_{en_node.pos}")
            dpg.add_group(tag=f"en_node_stats{en_node.pos}", parent=f"en_stat_list{en_node.pos}")
            dpg.add_text("Entry rate: " + str(round(en_node.rate, 4)), parent=f"en_node_stats{en_node.pos}", tag=f"en_node_rate{en_node.pos}")
            dpg.add_text("Current: 0p/s", parent=f"en_node_stats{en_node.pos}", tag=f"en_node_current{en_node.pos}")
            dpg.add_spacer(height=5, parent="stats")

        for i, repo in enumerate(self.circuit.repos):
            dpg.add_group(tag="repo_stat_list" + str(i), parent="stats", horizontal=True)
            dpg.add_drawlist(tag="repo_node_drawspace" + str(i), parent="repo_stat_list" + str(i), width=50, height=50)
            dpg.draw_rectangle(parent="repo_node_drawspace" + str(i), pmin=(0, 0), pmax=(25, 25), fill=repo.colour,
                               color=(0, 0, 0), tag=f"menu_rec_{repo.pos}")
            dpg.add_group(tag="repo_stats" + str(i), parent="repo_stat_list" + str(i))
            dpg.add_text(f"At {repo.pos}", parent="repo_stats" + str(i))
            dpg.add_text("Current: 0p/s", parent="repo_stats" + str(i), tag="repo_current" + str(i))
            dpg.add_spacer(height=5, parent="stats")

        for ex_node in self.circuit.exit_nodes:
            dpg.add_group(tag=f"ex_stat_list{ex_node.pos}", parent="stats", horizontal=True)
            dpg.add_drawlist(tag=f"ex_node_drawspace{ex_node.pos}", parent=f"ex_stat_list{ex_node.pos}", width=50, height=50)
            dpg.draw_rectangle(parent=f"ex_node_drawspace{ex_node.pos}", pmin=(0, 0), pmax=(25, 25), fill=(23, 240, 250),
                               color=(0, 0, 0), tag=f"menu_rec_{ex_node.pos}")
            dpg.add_group(tag=f"ex_node_stats{ex_node.pos}", parent=f"ex_stat_list{ex_node.pos}")
            dpg.add_text("Exit rate: " + str(round(-ex_node.rate, 4)), parent=f"ex_node_stats{ex_node.pos}", tag=f"ex_node_rate{ex_node.pos}")
            dpg.add_text("Current: 0p/s", parent=f"ex_node_stats{ex_node.pos}", tag=f"ex_node_current{ex_node.pos}")
            dpg.add_spacer(height=5, parent="stats")

        dpg.add_spacer(height=10, parent="stats")
        dpg.add_checkbox(label="Orange debug particles", parent="stats", callback=self.debug_mode)
        dpg.add_spacer(height=10, parent="stats")
        dpg.add_checkbox(label="Show co-ords", parent="stats", callback=self.show_coords)
        dpg.add_spacer(height=10, parent="stats")
        dpg.add_slider_int(label="Speed factor", parent="stats", width=100, min_value=1, max_value=5,
                           clamped=True, callback=self.speed_allocate, default_value=1, tag="speed_slider")

        dpg.add_spacer(height=10, parent="stats")
        dpg.add_button(label="?", callback=lambda: dpg.configure_item("help_window", show=True), parent="stats",
                       width=25, height=20)
        dpg.add_spacer(height=10, parent="stats")
        dpg.add_button(label="Pause process", width=200, height=30,
                       callback=self.pause_process, tag="pause_process_button",
                       parent="control")

        with dpg.item_handler_registry(tag="runtime_register") as handler:
            dpg.add_item_clicked_handler(callback=self.node_highlight, tag="highlight")
        dpg.bind_item_handler_registry("main_grid", "runtime_register")

    def node_highlight(self):
        mouse_pos = dpg.get_plot_mouse_pos()
        pos = (round(mouse_pos[0]), round(mouse_pos[1]))

        if pos == self.highlighted_pos:
            dpg.configure_item(f"menu_rec_{pos}", color=(0, 0, 0))
            self.highlighted_pos = None
        else:
            for n in self.circuit.entry_nodes + self.circuit.body:
                if n.pos == pos:
                    dpg.configure_item(f"menu_rec_{pos}", color=(200, 200, 0))
                    if self.highlighted_pos is not None:
                        dpg.configure_item(f"menu_rec_{self.highlighted_pos}", color=(0, 0, 0))
                    self.highlighted_pos = pos
                    break

    def pause_process(self):
        self.run = False
        dpg.delete_item("pause_process_button")
        dpg.add_button(label="Play process", width=200, height=30,
                       callback=self.play_process, tag="play_process_button",
                       parent="control")
        # TODO: show current graphs
        dpg.add_button(label="Graphical breakdown", width=200, height=30,
                       callback=self.reveal_graphs, tag="graphical_breakdown",
                       parent="control")
        dpg.add_button(label="Reset process", width=200, height=30,
                       callback=self.reset_process, tag="reset_process_button",
                       parent="control")

    def reset_process(self):
        dpg.delete_item("play_process_button")
        dpg.delete_item("reset_process_button")
        # Finish TASEP process loop (different from pausing)
        self.alive = False
        for p in self.circuit.particles:
            dpg.delete_item("particle" + str(p.no))
        self.circuit.particles = []

        dpg.delete_item("stats")

        self.currents_displayer.cancel()

        for n in self.circuit.entry_nodes + self.circuit.body:
            n.check_in = []
            n.count = 0

        for item in self.hidden:
            dpg.configure_item(item, show=True)

        dpg.delete_item("highlight")
        dpg.delete_item("runtime_register")
        dpg.bind_item_handler_registry("main_grid", "plot_register")

    def reveal_graphs(self):
        pass

    def play_process(self):
        self.run = True
        dpg.delete_item("play_process_button")
        dpg.delete_item("reset_process_button")
        dpg.add_button(label="Pause process", width=200, height=30,
                       callback=self.pause_process, tag="pause_process_button",
                       parent="control")


    def start(self):
        tasep_process = Thread(name="tasep process", target=self.run_tasep, daemon=True)
        self.currents_displayer = RepeatTimer(3, self.display_currents)
        tasep_process.start()
        self.currents_displayer.start()

    def debug_mode(self):
        self.debug_particle = not self.debug_particle

    def show_coords(self):
        self.coords = not self.coords

    def speed_allocate(self, sender):
        self.speed_factor = dpg.get_value(sender)


class CurrentGraphs:
    def __init__(self, nodes):
        self.n = nodes


