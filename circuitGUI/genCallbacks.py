import dearpygui.dearpygui as dpg
import circuitOperations
import threading
import drawCallbacks
import interfaceObjects

global circuit_image

class RepeatTimer(threading.Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)


def gen_circuit():
    """Callback function for 'Generate circuit' button. TASEP dispatcher specifically in this case."""
    global tcd, circuit, circuit_image
    dpg.delete_item("gen_circuit_button")
    dpg.delete_item("draw_circuit_button")
    dpg.add_text("Loading...", parent="control", tag="loading_text")

    dpg.configure_item("plot_handler", callback=get_pos)

    # Create an instance of the TASEP circuit dispatcher object
    tcd = circuitOperations.TasepCircuitDispatcherGUI()
    # Method returns skeleton of generated circuit (skeleton because no paths yet generated)
    circuit = tcd.gen_circuit()
    # Instance of circuit image generated
    circuit_image = interfaceObjects.CircuitImage(circuit)
    # Draw path-less circuit
    circuit_image.show_nodes()

    dpg.delete_item("loading_text")
    dpg.add_button(label="Generate paths", width=200, height=30, parent="control",
                   tag="gen_paths_button", callback=paths_gen)
    dpg.add_button(label="WIPE CIRCUIT", width=200, height=30, parent="control",
                   tag="circuit_wiper_button", callback=wipe_circuit)

def get_pos():
    global circuit
    mouse_pos = dpg.get_plot_mouse_pos()
    pos = (round(mouse_pos[0]), round(mouse_pos[1]))
    print()
    print(f"path_space: {circuit.path_space[pos]}")
    print(f"orientation: {circuit.path_orientation[pos]}")
    if pos in circuit.undercurrent_space:
        print(f"undercurrent_space: {circuit.undercurrent_space[pos]}")


def wipe_circuit():
    global circuit_image
    dpg.add_text("Loading...", parent="control", tag="loading_text")

    # Wipe buttons
    dpg.delete_item("gen_paths_button")
    dpg.delete_item("circuit_wiper_button")
    dpg.delete_item("wipe_paths_button")
    dpg.delete_item("start_process_button")

    # Wipe features
    circuit_image.hide_nodes()
    circuit_image.hide_paths()

    # Finish wipe
    dpg.delete_item("loading_text")
    draw_button = dpg.add_button(label="Draw circuit", width=200, height=30,
                                callback=drawCallbacks.draw_mode, tag="draw_circuit_button", parent="control")
    gen_button = dpg.add_button(label="Generate circuit", width=200, height=30,
                                callback=gen_circuit, tag="gen_circuit_button", parent="control")

    circuit.branches = 0


def paths_gen():
    global circuit_image

    # Generate and draw paths
    res = False
    while not res:
        res = circuit.gen_circuit_paths()
    circuit_image.show_paths()

    # Deletes path gen button
    dpg.delete_item("gen_paths_button")
    # Adds path wipe button
    dpg.add_button(label="Wipe paths", width=200, height=30,
                    callback=wipe_paths, tag="wipe_paths_button",
                    parent="control", before="circuit_wiper_button")
    # Button to start process
    dpg.add_button(label="Start process", width=200, height=30,
                   callback=intiate_process, tag="start_process_button",
                   parent="control", before="wipe_paths_button")

def wipe_paths():
    global circuit_image
    dpg.delete_item("wipe_paths_button")
    circuit.wipe_paths()

    circuit_image.hide_paths()

    dpg.add_button(label="Generate paths", width=200, height=30, parent="control",
                   tag="gen_paths_button", callback=paths_gen, before="circuit_wiper_button")
    dpg.delete_item("start_process_button")

def intiate_process():
    global currents_displayer
    dpg.delete_item("start_process_button")
    dpg.delete_item("circuit_wiper_button")
    dpg.delete_item("wipe_paths_button")

    dpg.add_group(tag="stats", parent="control")

    for en_node in circuit.entry_nodes:
        dpg.add_group(tag="en_stat_list0", parent="stats", horizontal=True)
        dpg.add_drawlist(tag="en_node_drawspace0", parent="en_stat_list0", width=50, height=50)
        dpg.draw_rectangle(parent="en_node_drawspace0", pmin=(0, 0), pmax=(25, 25), fill=(233, 240, 50),
                           color=(0,0,0))
        dpg.add_group(tag="en_node_stats0", parent="en_stat_list0")
        dpg.add_text("Entry rate: " + str(round(en_node.rate, 4)), parent="en_node_stats0", tag="en_node_rate0")
        dpg.add_text("Current: 0p/s", parent="en_node_stats0", tag="en_node_current0")
        dpg.add_spacer(height=5, parent="stats")

    for i, repo in enumerate(circuit.repos):
        dpg.add_group(tag="repo_stat_list" + str(i), parent="stats", horizontal=True)
        dpg.add_drawlist(tag="repo_node_drawspace" + str(i), parent="repo_stat_list" + str(i), width=50, height=50)
        dpg.draw_rectangle(parent="repo_node_drawspace" + str(i), pmin=(0, 0), pmax=(25, 25), fill=(233, 12, 50),
                           color=(0, 0, 0))
        dpg.add_group(tag="repo_stats" + str(i), parent="repo_stat_list" + str(i))
        dpg.add_text("No." + str(i+1), parent="repo_stats" + str(i), tag="repo_number" + str(i))
        dpg.add_text("Current: 0p/s", parent="repo_stats" + str(i), tag="repo_current" + str(i))
        dpg.add_spacer(height=5, parent="stats")

    for ex_node in circuit.exit_nodes:
        dpg.add_group(tag="ex_stat_list0", parent="stats", horizontal=True)
        dpg.add_drawlist(tag="ex_node_drawspace0", parent="ex_stat_list0", width=50, height=50)
        dpg.draw_rectangle(parent="ex_node_drawspace0", pmin=(0, 0), pmax=(25, 25), fill=(23, 240, 250),
                           color=(0, 0, 0))
        dpg.add_group(tag="ex_node_stats0", parent="ex_stat_list0")
        dpg.add_text("Exit rate: " + str(round(-ex_node.rate, 4)), parent="ex_node_stats0", tag="ex_node_rate0")
        dpg.add_text("Current: 0p/s", parent="ex_node_stats0", tag="ex_node_current0")
        dpg.add_spacer(height=5, parent="stats")

    dpg.add_spacer(height=10, parent="stats")
    dpg.add_checkbox(label="Orange debug particles", parent="stats", callback=debug_mode)
    dpg.add_spacer(height=10, parent="stats")
    dpg.add_slider_int(label="Speed factor", parent="stats", width=100, min_value=1, max_value=5,
                       clamped=True, callback=speed_allocate, default_value=1, tag="speed_slider")

    dpg.add_spacer(height=10, parent="stats")
    dpg.add_button(label="?", callback=lambda: dpg.configure_item("help_window", show=True), parent="stats",
                   width=25, height=20)
    dpg.add_spacer(height=10, parent="stats")

    tasep_process = threading.Thread(name="tasep process", target=tcd.run_tasep, daemon=True)
    currents_displayer = RepeatTimer(3, tcd.display_currents)
    tasep_process.start()
    currents_displayer.start()
    dpg.add_button(label="Pause process", width=200, height=30,
                   callback=pause_process, tag="pause_process_button",
                   parent="control")

def pause_process():
    tcd.run = False
    dpg.delete_item("pause_process_button")
    dpg.add_button(label="Play process", width=200, height=30,
                   callback=play_process, tag="play_process_button",
                   parent="control")
    dpg.add_button(label="Reset process", width=200, height=30,
                   callback=reset_process, tag="reset_process_button",
                   parent="control")

def play_process():
    tcd.run = True
    dpg.delete_item("play_process_button")
    dpg.delete_item("reset_process_button")
    dpg.add_button(label="Pause process", width=200, height=30,
                   callback=pause_process, tag="pause_process_button",
                   parent="control")

def reset_process():
    dpg.delete_item("play_process_button")
    dpg.delete_item("reset_process_button")
    tcd.alive = False
    for p in circuit.particles:
        dpg.delete_item("particle" + str(p.no))
    circuit.particles = []

    dpg.delete_item("stats")

    currents_displayer.cancel()

    for n in circuit.entry_nodes + circuit.body:
        n.check_in = []
        n.count = 0

    # Adds wipe circuit button
    dpg.add_button(label="WIPE CIRCUIT", width=200, height=30, parent="control",
                   tag="circuit_wiper_button", callback=wipe_circuit)
    # Adds path wipe button
    dpg.add_button(label="Wipe paths", width=200, height=30,
                   callback=wipe_paths, tag="wipe_paths_button",
                   parent="control", before="circuit_wiper_button")
    # Button to start process
    dpg.add_button(label="Start process", width=200, height=30,
                   callback=intiate_process, tag="start_process_button",
                   parent="control", before="wipe_paths_button")

def debug_mode():
    tcd.debug_particle = not tcd.debug_particle

def speed_allocate(sender):
    tcd.speed_factor = dpg.get_value(sender)
