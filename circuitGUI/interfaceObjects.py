import dearpygui.dearpygui as dpg
import threading
from math import floor
import numpy as np
import time

import circuitOperations.circuitDispatchers as circuitDispatchers
from circuitOperations.circuitObjects import Particle, DataRecorder



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
                            if pos in path_space[a]:
                                if pos in circuit.undercurrent_space:
                                    if circuit.undercurrent_orientation[pos] == circuit.path_orientation[a]:
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

    def run_tasep(self):
        """"TASEP dispatcher modified for dearpygui"""

        rng = np.random.default_rng()
        self.run = True
        self.alive = True
        self.speed_factor = 1
        self.debug_particle = False
        self.particle_count = 0
        self.play_time = 0

        # Shorthand
        c = self.circuit
        while self.alive:
            while self.run:
                option_size = len(c.entry_nodes) + len(c.particles)
                wait_factor = rng.exponential(1 / (self.speed_factor * option_size))
                self.play_time += rng.exponential(1/option_size)
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
                                if self.particle_count % 10 == 0 and self.debug_particle:
                                    col = (255, 100, 0)
                                else:
                                    col = (255, 255, 255)
                                dpg.draw_circle(chosen.pos, 0.3, fill=col, parent="main_grid",
                                                tag="particle" + str(self.particle_count))
                                self.particle_count += 1
                                chosen.count += 1
                                chosen.take(self.play_time)

                if chosen.name == "particle":
                    # If in exit node we take off the circuit with p. rate
                    for ex in c.exit_nodes:
                        if ex.pos == chosen.pos:
                            if rng.random() <= -ex.rate:
                                self.circuit.particles.remove(chosen)
                                dpg.delete_item("particle" + str(chosen.no))
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
                            dpg.delete_item("particle" + str(chosen.no))
                            if chosen.orientation == self.circuit.path_orientation[
                                next_pos] or self.circuit.in_exit_node(next_pos):
                                if chosen.no % 10 == 0 and self.debug_particle:
                                    col = (255, 100, 0)
                                else:
                                    col = (255, 255, 255)
                                dpg.draw_circle(next_pos, 0.3, fill=col, parent="main_grid",
                                                tag="particle" + str(chosen.no))
                            for n in self.circuit.body:
                                if n.pos == next_pos:
                                    n.count += 1
                                    self.lock.acquire()
                                    n.take(self.play_time)
                                    self.lock.release()
                                    if n.name == "repo":
                                        dpg.configure_item(f"repo_text_{n.pos}", text=n.count)
                                    break

    def display_currents(self):
        if self.run:
            for node in self.tracked:
                if node.count != 0:
                    self.lock.acquire()
                    count = floor(node.check_in[0])
                    top = floor(node.check_in[-1])
                    if top != count:
                        # Keep track for displayed average calculation
                        second_currents = [0]
                        for i, t in enumerate(node.check_in):
                            f = floor(t)
                            while count != f:
                                count += 1
                                self.data.currents_1[node.pos].append(0)
                                second_currents.append(0)
                            else:
                                if count != top:
                                    self.data.currents_1[node.pos][-1] += 1
                                    second_currents[-1] += 1
                        node.check_in = node.check_in[i:]
                        display_avg = round(sum(second_currents)/len(second_currents), 3)
                        dpg.configure_item(f"node_current{node.pos}",
                                           default_value=f"Current: {display_avg}p/s")
                    self.lock.release()

    def draw_control_menu(self):
        dpg.add_group(tag="stats", parent="control")
        dpg.add_spacer(height=2, parent="stats")
        dpg.add_text("Click node on grid\nto identify:", parent="stats", indent=40, tag="click_explainer")
        dpg.add_spacer(height=9, parent="stats")
        # FIXME: could be one for loop through self.tracked. Neater; line efficient.
        for en_node in self.circuit.entry_nodes:
            if en_node.track:
                dpg.add_group(tag=f"en_stat_list{en_node.pos}", parent="stats", horizontal=True)
                dpg.add_drawlist(tag=f"en_node_drawspace{en_node.pos}", parent=f"en_stat_list{en_node.pos}", width=50, height=50)
                dpg.draw_rectangle(parent=f"en_node_drawspace{en_node.pos}", pmin=(0, 0), pmax=(25, 25), fill=(233, 240, 50),
                                   color=(0, 0, 0), tag=f"menu_rec_{en_node.pos}")
                dpg.add_group(tag=f"en_node_stats{en_node.pos}", parent=f"en_stat_list{en_node.pos}")
                dpg.add_text("Entry rate: " + str(round(en_node.rate, 4)), parent=f"en_node_stats{en_node.pos}", tag=f"en_node_rate{en_node.pos}")
                dpg.add_text("Current: 0p/s", parent=f"en_node_stats{en_node.pos}", tag=f"node_current{en_node.pos}")
                dpg.add_spacer(height=5, parent="stats")

        for i, repo in enumerate(self.circuit.repos):
            if repo.track:
                dpg.add_group(tag="repo_stat_list" + str(i), parent="stats", horizontal=True)
                dpg.add_drawlist(tag="repo_node_drawspace" + str(i), parent="repo_stat_list" + str(i), width=50, height=50)
                dpg.draw_rectangle(parent="repo_node_drawspace" + str(i), pmin=(0, 0), pmax=(25, 25), fill=repo.colour,
                                   color=(0, 0, 0), tag=f"menu_rec_{repo.pos}")
                dpg.add_group(tag="repo_stats" + str(i), parent="repo_stat_list" + str(i))
                dpg.add_text(f"At {repo.pos}", parent="repo_stats" + str(i))
                dpg.add_text("Current: 0p/s", parent="repo_stats" + str(i), tag=f"node_current{repo.pos}")
                dpg.add_spacer(height=5, parent="stats")

        for ex_node in self.circuit.exit_nodes:
            if ex_node.track:
                dpg.add_group(tag=f"ex_stat_list{ex_node.pos}", parent="stats", horizontal=True)
                dpg.add_drawlist(tag=f"ex_node_drawspace{ex_node.pos}", parent=f"ex_stat_list{ex_node.pos}", width=50, height=50)
                dpg.draw_rectangle(parent=f"ex_node_drawspace{ex_node.pos}", pmin=(0, 0), pmax=(25, 25), fill=(23, 240, 250),
                                   color=(0, 0, 0), tag=f"menu_rec_{ex_node.pos}")
                dpg.add_group(tag=f"ex_node_stats{ex_node.pos}", parent=f"ex_stat_list{ex_node.pos}")
                dpg.add_text("Exit rate: " + str(round(-ex_node.rate, 4)), parent=f"ex_node_stats{ex_node.pos}", tag=f"ex_node_rate{ex_node.pos}")
                dpg.add_text("Current: 0p/s", parent=f"ex_node_stats{ex_node.pos}", tag=f"node_current{ex_node.pos}")
                dpg.add_spacer(height=5, parent="stats")



        dpg.add_spacer(height=10, parent="stats")
        dpg.add_checkbox(label="Orange debug particles", parent="stats", callback=self.debug_mode)
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
                if not self.run:
                    dpg.delete_item("particular_graph")
                self.highlighted_pos = None
        else:
            for n in self.tracked:
                if n.pos == pos:
                    dpg.configure_item(f"menu_rec_{pos}", color=(200, 200, 0))
                    if self.highlighted_pos is not None:
                        dpg.configure_item(f"menu_rec_{self.highlighted_pos}", color=(0, 0, 0))
                        if not self.run:
                            dpg.delete_item("particular_graph")
                    if not self.run:
                        dpg.add_button(label="Show graph", width=200, height=30,
                                       callback=self.reveal_graph, tag="particular_graph",
                                       parent="control", before="graphical_breakdown", user_data=n)
                    self.highlighted_pos = pos
                    break


    def pause_process(self):
        self.data.calc_currents()

        self.run = False
        dpg.delete_item("pause_process_button")
        dpg.add_button(label="Play process", width=200, height=30,
                       callback=self.play_process, tag="play_process_button",
                       parent="control")
        if self.tracked:
            dpg.add_button(label="Show all graphs", width=200, height=30,
                           callback=self.reveal_graphs, tag="graphical_breakdown",
                           parent="control")
        dpg.add_button(label="Reset process", width=200, height=30,
                       callback=self.reset_process, tag="reset_process_button",
                       parent="control")
        dpg.set_value("click_explainer", "Click node on grid\nto show stats/graph:")

    def reset_process(self):
        dpg.delete_item("play_process_button")
        dpg.delete_item("reset_process_button")
        dpg.delete_item("graphical_breakdown")
        if self.highlighted_pos is not None:
            dpg.delete_item("particular_graph")
        # Finish TASEP process loop (different from pausing)
        self.alive = False
        for p in self.circuit.particles:
            dpg.delete_item("particle" + str(p.no))
        self.circuit.particles = []

        dpg.delete_item("stats")

        self.currents_displayer.cancel()

        for n in self.circuit.entry_nodes + self.circuit.body:
            n.check_in = [0]
            n.count = 0

        for item in self.hidden:
            dpg.configure_item(item, show=True)

        dpg.delete_item("highlight")
        dpg.delete_item("runtime_register")
        dpg.bind_item_handler_registry("main_grid", "plot_register")

        print(self.circuit.particles)

    def reveal_graphs(self):
        dpg.delete_item("reset_process_button")
        dpg.delete_item("graphical_breakdown")
        dpg.delete_item("play_process_button")

        if self.highlighted_pos is not None:
            dpg.delete_item("particular_graph")

        dpg.configure_item("main_grid", show=False)

        data_display = StatisticalFrames(self.data)
        data_display.setup_frames()

        dpg.add_button(label="Back", width=200, height=30,
                       callback=self.exit_graphs, tag="exit_graphs",
                       parent="control")

    def reveal_graph(self, sender, app_data, user_data):
        dpg.delete_item("reset_process_button")
        dpg.delete_item("graphical_breakdown")
        dpg.delete_item("particular_graph")
        dpg.delete_item("play_process_button")
        node = user_data
        dpg.configure_item("main_grid", show=False)

        data_display = StatisticalFrames(self.data)
        data_display.setup_frames(pos_array = [node.pos])

        dpg.add_button(label="Back", width=200, height=30,
                       callback=self.exit_graphs, tag="exit_graphs",
                       parent="control")

    def exit_graphs(self):
        dpg.delete_item("exit_graphs")
        dpg.delete_item("stat_frames")
        dpg.configure_item("main_grid", show=True)
        dpg.add_button(label="Play process", width=200, height=30,
                       callback=self.play_process, tag="play_process_button",
                       parent="control")
        dpg.add_button(label="Show all graphs", width=200, height=30,
                       callback=self.reveal_graphs, tag="graphical_breakdown",
                       parent="control")
        if self.highlighted_pos is not None:
            for node in self.circuit.body + self.circuit.entry_nodes:
                if node.pos == self.highlighted_pos:
                    dpg.add_button(label="Show graph", width=200, height=30,
                                   callback=self.reveal_graph, tag="particular_graph",
                                   parent="control", before="graphical_breakdown", user_data=node)
        dpg.add_button(label="Reset process", width=200, height=30,
                       callback=self.reset_process, tag="reset_process_button",
                       parent="control")


    def play_process(self):
        self.run = True
        dpg.delete_item("play_process_button")
        dpg.delete_item("reset_process_button")
        dpg.delete_item("graphical_breakdown")
        if self.highlighted_pos is not None:
            dpg.delete_item("particular_graph")
        dpg.add_button(label="Pause process", width=200, height=30,
                       callback=self.pause_process, tag="pause_process_button",
                       parent="control")


    def start(self):
        # Establish which nodes to track
        for n in self.circuit.entry_nodes + self.circuit.body:
            if n.track:
                self.tracked.append(n)
        self.data = DataRecorder(self.tracked)

        # Create lock to avoid errors in threading
        self.lock = threading.Lock()

        # Establish and run TASEP thread and independent currents calculator
        tasep_process = Thread(name="tasep process", target=self.run_tasep, daemon=True)
        self.currents_displayer = RepeatTimer(3, self.display_currents)
        tasep_process.start()
        self.currents_displayer.start()


    def debug_mode(self):
        self.debug_particle = not self.debug_particle

    def speed_allocate(self, sender):
        self.speed_factor = dpg.get_value(sender)


class StatisticalFrames:
    def __init__(self, data):
        self._data = data
        self.loaded = None

    def setup_frames(self, pos_array = None):
        dpg.add_group(before="control", tag="stat_frames")
        dpg.add_tab_bar(tag="pos_tab_bar", parent="stat_frames")
        dpg.add_group(tag="info", parent="stat_frames")
        dpg.add_text("Click coloured squares of legend items to hide/show.", parent="info")

        if pos_array is None:
            pos_array = [n.pos for n in self._data.nodes]

        for pos in pos_array:
            dpg.add_tab_button(tag=f"{pos}_tab", label=pos, parent="pos_tab_bar",
                               callback=self.load_current_data, user_data=pos)

        self.create_current_plot(pos_array[0])
        self.loaded = pos_array[0]
        dpg.configure_item(f"{self.loaded}_tab", label="V")

    def load_current_data(self, sender, app_data, user_data):
        pos = user_data
        tag = f"{pos}_current_plot"
        if pos != self.loaded:
            dpg.configure_item(f"{self.loaded}_current_plot", show=False)
            dpg.configure_item(f"{self.loaded}_tab", label=self.loaded)
            dpg.configure_item(f"{pos}_tab", label="V")
            if dpg.does_item_exist(tag):
                dpg.configure_item(tag, show=True)
            else:
                self.create_current_plot(pos)
            self.loaded = pos
    def create_current_plot(self, pos):
        dpg.add_plot(label=f"Current at {pos}", height=800, width=1600, tag=f"{pos}_current_plot", parent="info")
        # optionally create legend
        dpg.add_plot_legend(parent=f"{pos}_current_plot")
        # Load data to display
        y_10 = self._data.currents_10[pos]
        y_50 = self._data.currents_50[pos]
        x_10 = [10*x for x in range(len(y_10))]
        x_50 = [50*x for x in range(len(y_50))]
        # REQUIRED: create x and y axes
        ax_x = dpg.add_plot_axis(axis=0, label="Time - s", parent=f"{pos}_current_plot", lock_min=False,
                                 lock_max=False)
        dpg.add_plot_axis(axis=1, label="Current - p/s", parent=f"{pos}_current_plot", tag=f"{pos}_y_axis")
        dpg.fit_axis_data(axis=ax_x)
        #dpg.set_axis_limits(axis=ax_x, ymin=0, ymax=x_10[-1])



        avg_line = [sum(y_10)/len(y_10) for i in range(len(y_10))]
        dpg.add_line_series(x_50, y_50, parent=f"{pos}_y_axis", label="Intervals of 50")
        dpg.add_line_series(x_10, y_10, parent=f"{pos}_y_axis", label="Intervals of 10")
        dpg.add_hline_series(avg_line, parent=f"{pos}_y_axis", label=f"{round(avg_line[0], 5)}")

