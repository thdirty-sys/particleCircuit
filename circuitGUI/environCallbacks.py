import dearpygui.dearpygui as dpg
import circuitOperations

path_rec_count = 0
def gen_circuit():
    """Callback function for 'Generate circuit' button. TASEP dispatcher specifically in this case."""
    dpg.delete_item("gen_circuit_button")
    dpg.add_text("Loading...", parent="control", tag="loading_text")

    # Create an instance of the TASEP circuit dispatcher object
    tcd = circuitOperations.TasepCircuitDispatcher()
    # Method returns skeleton of generated circuit (skeleton because no paths yet generated)
    global circuit
    circuit = tcd.gen_circuit()

    # Draw each feature
    for i, repo in enumerate(circuit.repos):
        dpg.draw_rectangle(pmin=repo.pos, pmax=repo.pos, parent="main_grid",
                           color=(233, 12, 50), tag="rep_" + str(i), label=repo.count)

    for i, en_node in enumerate(circuit.entry_nodes):
        dpg.draw_rectangle(pmin=en_node.pos, pmax=en_node.pos, parent="main_grid",
                           color=(233, 240, 50), tag="entry_node" + str(i), label=str(en_node.rate))

    for i, ex_node in enumerate(circuit.exit_nodes):
        dpg.draw_rectangle(pmin=ex_node.pos, pmax=ex_node.pos, parent="main_grid",
                           color=(23, 240, 250), tag="exit_node" + str(i), label=str(ex_node.rate))

    dpg.delete_item("loading_text")
    dpg.add_button(label="Generate paths", width=200, height=30, parent="control",
                   tag="gen_paths_button", callback=paths_gen)
    dpg.add_button(label="WIPE CIRCUIT", width=200, height=30, parent="control",
                   tag="circuit_wiper_button", callback=wipe_circuit)


def wipe_circuit():
    dpg.add_text("Loading...", parent="control", tag="loading_text")

    #Wipe buttons
    dpg.delete_item("gen_paths_button")
    dpg.delete_item("circuit_wiper_button")

    # Wipe features
    for i in range(len(circuit.repos)):
        dpg.delete_item("rep_" + str(i))

    for i in range(len(circuit.entry_nodes)):
        dpg.delete_item("entry_node" + str(i))

    for i in range(len(circuit.exit_nodes)):
        dpg.delete_item("exit_node" + str(i))

    for i in range(path_rec_count):
        dpg.delete_item("path_block" + str(i))

    """count = 0
    for pos in circuit.path_space:
        if circuit.path_space[pos] != []:
            dpg.delete_item("path_block" + str(count))
            count += 1"""


    # Finish wipe
    dpg.delete_item("loading_text")
    gen_button = dpg.add_button(label="Generate circuit", width=150, height=20,
                                callback=gen_circuit, tag="gen_circuit_button", parent="control")

    circuit.branches = 0

def paths_gen():
    global path_rec_count

    # Generate and draw paths
    res = circuit.gen_circuit_paths()
    if res:
        path_elements = circuit.path_space
        path_rec_count = 0
        for pos in path_elements:
            if path_elements[pos] != [] and (not circuit.in_repo(pos)) and (not circuit.in_node(pos)):
                if int(circuit.path_orientation[pos]) > 60:
                    col = (3,40,255)
                else:
                    col = (min(255, int(circuit.path_orientation[pos])*255/(len(circuit.repos)-1)), 50, 0)
                dpg.draw_rectangle(pmin=pos, pmax=pos, parent="main_grid", color=col, tag="path_block" + str(path_rec_count))
                path_rec_count += 1

        print(circuit.branches)
    else:
        wipe_circuit()