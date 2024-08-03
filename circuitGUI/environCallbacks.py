import dearpygui.dearpygui as dpg
import circuitOperations



def gen_circuit():
    """Callback function for 'Generate circuit' button. TASEP dispatcher specifically in this case."""
    dpg.delete_item("gen_circuit_button")
    dpg.add_text("Loading...", parent="control", tag="loading_text")

    # Create an instance of the TASEP circuit dispatcher object
    global tcd
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

    # Wipe buttons
    dpg.delete_item("gen_paths_button")
    dpg.delete_item("circuit_wiper_button")
    dpg.delete_item("wipe_paths_button")
    dpg.delete_item("start_process_button")

    # Wipe features
    for i in range(len(circuit.repos)):
        dpg.delete_item("rep_" + str(i))

    for i in range(len(circuit.entry_nodes)):
        dpg.delete_item("entry_node" + str(i))

    for i in range(len(circuit.exit_nodes)):
        dpg.delete_item("exit_node" + str(i))

    for i in range(path_rec_count):
        dpg.delete_item("path_block" + str(i))

    for i in range(sep_line_count):
        dpg.delete_item("sep_line" + str(i))

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

def valid_adjacents(pos):
    """Given a position value, return adjacent positions which are in the valid range"""
    x, y = pos
    adjacent_pos = [(x+1, y), (x, y-1), (x, y+1), (x-1, y)]
    for p in adjacent_pos:
        a, b = p
        if a < 0 or b < 0 or a > 49 or b > 25:
            adjacent_pos.remove(p)
    return adjacent_pos


def draw_sep_line(w ,v):
    w_x, w_y = w
    v_x, v_y = v

    if w_x - v_x == 0:
        line_y = min(v_y, w_y) + 0.5
        dpg.draw_line((v_x-0.55, line_y), (v_x+0.55, line_y), color=(0,0,0, 255), parent="main_grid",
                      tag="sep_line" + str(sep_line_count), thickness=0.08)
    else:
        line_x = min(v_x, w_x) + 0.5
        dpg.draw_line((line_x, v_y-0.55), (line_x, v_y+0.55), color=(0, 0, 0, 255), parent="main_grid",
                      tag="sep_line" + str(sep_line_count), thickness=0.08)


def paths_gen():
    global path_rec_count
    global sep_line_count

    # Generate and draw paths
    res = circuit.gen_circuit_paths()
    path_elements = circuit.path_space
    path_rec_count = 0
    sep_line_count = 0
    for pos in path_elements:
        if path_elements[pos] != [] and (not circuit.in_repo(pos)) and (not circuit.in_node(pos)):
            # Set colour grading for different node orientations
            l = len(circuit.body)
            o = int(circuit.path_orientation[pos])
            col = ((o+1)*255/(l), 50, 100)

            # Draw rectangle
            dpg.draw_rectangle(pmin=pos, pmax=pos, parent="main_grid", color=col,
                               tag="path_block" + str(path_rec_count))
            path_rec_count += 1

            adjacent = valid_adjacents(pos)
            for a in adjacent:
                if not circuit.in_repo(a) and not circuit.in_node(a):
                    if a not in path_elements[pos] and pos not in path_elements[a]:
                        draw_sep_line(pos, a)
                        sep_line_count += 1
                    else:
                        if circuit.path_orientation[pos] != circuit.path_orientation[a]:
                            if pos in circuit.splits:
                                if a not in circuit.splits[pos]:
                                    draw_sep_line(pos, a)
                                    sep_line_count += 1
                            elif a in circuit.splits:
                                if pos not in circuit.splits[a]:
                                    draw_sep_line(pos, a)
                                    sep_line_count += 1
                            else:
                                draw_sep_line(pos, a)
                                sep_line_count += 1

    # Deal with sep lines for nodes
    for node in circuit.entry_nodes + circuit.body:
        adjacent = valid_adjacents(node.pos)
        for a in adjacent:
            if node.pos in path_elements[a] or a in path_elements[node.pos]:
                draw_sep_line(node.pos, a)
                sep_line_count += 1




    # Deletes path gen button
    dpg.delete_item("gen_paths_button")
    # Adds path wipe button
    dpg.add_button(label="Wipe paths", width=150, height=20,
                    callback=wipe_paths, tag="wipe_paths_button",
                    parent="control", before="circuit_wiper_button")
    # Button to start process
    dpg.add_button(label="Start process", width=150, height=20,
                   callback=intiate_process, tag="start_process_button",
                   parent="control", before="wipe_paths_button")

def wipe_paths():
    dpg.delete_item("wipe_paths_button")
    circuit.wipe_paths()
    for i in range(path_rec_count):
        dpg.delete_item("path_block" + str(i))
    dpg.add_button(label="Generate paths", width=200, height=30, parent="control",
                   tag="gen_paths_button", callback=paths_gen, before="circuit_wiper_button")
    dpg.delete_item("start_process_button")

def intiate_process():
    tcd.run_tasep()