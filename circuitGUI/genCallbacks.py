import dearpygui.dearpygui as dpg
import drawCallbacks
import interfaceObjects
import circuitOperations


def gen_circuit():
    """Callback function for 'Generate circuit' button. TASEP dispatcher specifically in this case."""
    global tcd, circuit, circuit_image, circ_generator
    dpg.delete_item("gen_circuit_button")
    dpg.delete_item("draw_circuit_button")
    dpg.add_text("Loading...", parent="control", tag="loading_text")

    dpg.configure_item("plot_handler", callback=get_pos)

    # Create an instance of the TASEP circuit dispatcher object
    tcd = interfaceObjects.TasepCircuitDispatcherGUI()
    # Method returns skeleton of generated circuit (skeleton because no paths yet generated)
    circ_generator = circuitOperations.RandomCompleteCircuitGenerator()
    circuit = circ_generator.gen_circuit()
    # set circuit for TASEP to act on
    tcd.circuit = circuit
    # Instance of circuit image generated
    circuit_image = interfaceObjects.CircuitImage(circuit)
    # Draw path-less circuit
    circuit_image.show_nodes()

    dpg.delete_item("loading_text")
    dpg.add_button(label="Generate paths", width=200, height=30, parent="control",
                   tag="gen_paths_button", callback=paths_gen)
    dpg.add_button(label="Wipe circuit", width=200, height=30, parent="control",
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
        res = circ_generator.gen_circuit_paths()
    circuit_image.show_paths()

    # Deletes path gen button
    dpg.delete_item("gen_paths_button")
    # Adds path wipe button
    dpg.add_button(label="Wipe paths", width=200, height=30,
                    callback=wipe_paths, tag="wipe_paths_button",
                    parent="control", before="circuit_wiper_button")
    # Button to start process
    dpg.add_button(label="Start process", width=200, height=30,
                   callback=initiate_process, tag="start_process_button",
                   parent="control", before="wipe_paths_button")

def wipe_paths():
    global circuit_image
    dpg.delete_item("wipe_paths_button")
    circuit.reset_paths()

    circuit_image.hide_paths()

    dpg.add_button(label="Generate paths", width=200, height=30, parent="control",
                   tag="gen_paths_button", callback=paths_gen, before="circuit_wiper_button")
    dpg.delete_item("start_process_button")

def initiate_process():
    dpg.configure_item("start_process_button", show=False)
    dpg.configure_item("circuit_wiper_button", show=False)
    dpg.configure_item("wipe_paths_button", show=False)

    tcd.draw_control_menu()
    tcd.hidden = ["start_process_button", "circuit_wiper_button", "wipe_paths_button"]
    tcd.start()
