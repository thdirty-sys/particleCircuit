from math import floor
import dearpygui.dearpygui as dpg
import threading
from circuitGUI import genCallbacks, interfaceObjects
import circuitOperations

saved_hover_pos = None

class RepeatTimer(threading.Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)


def draw_mode():
    global current_brush, c, circuit_image, caretaker
    current_brush = "off"

    dpg.delete_item("gen_circuit_button")
    dpg.delete_item("draw_circuit_button")

    dpg.add_group(tag="brushes_menu", parent="control")

    dpg.add_spacer(height=20, parent="brushes_menu")
    dpg.add_group(tag="entry_node_bar", parent="brushes_menu", horizontal=True)
    dpg.add_spacer(width=10, parent="entry_node_bar")
    dpg.add_drawlist(tag="entry_node_icon", parent="entry_node_bar", width=30, height=50)
    dpg.draw_rectangle(parent="entry_node_icon", pmin=(0, 0), pmax=(25, 25), fill=(233, 240, 50),
                       color=(0, 0, 0), tag="entry_brush_rec", thickness=2)
    dpg.add_text("Entry node", parent="entry_node_bar")
    dpg.add_spacer(height=10, parent="brushes_menu")

    dpg.add_group(tag="repo_node_bar", parent="brushes_menu", horizontal=True)
    dpg.add_spacer(width=10, parent="repo_node_bar")
    dpg.add_drawlist(tag="repo_node_icon", parent="repo_node_bar", width=30, height=50)
    dpg.draw_rectangle(parent="repo_node_icon", pmin=(0, 0), pmax=(25, 25), fill=(233, 12, 50),
                       color=(0, 0, 0), tag="repo_brush_rec", thickness=2)
    dpg.add_text("Repository", parent="repo_node_bar")
    dpg.add_spacer(height=10, parent="brushes_menu")

    dpg.add_group(tag="exit_node_bar", parent="brushes_menu", horizontal=True)
    dpg.add_spacer(width=10, parent="exit_node_bar")
    dpg.add_drawlist(tag="exit_node_icon", parent="exit_node_bar", width=30, height=50)
    dpg.draw_rectangle(parent="exit_node_icon", pmin=(0, 0), pmax=(25, 25), fill=(23, 240, 250),
                       color=(0, 0, 0), tag="exit_brush_rec", thickness=2)
    dpg.add_text("Exit node", parent="exit_node_bar")
    dpg.add_spacer(height=10, parent="brushes_menu")

    dpg.add_group(tag="path_node_bar", parent="brushes_menu", horizontal=True)
    dpg.add_spacer(width=10, parent="path_node_bar")
    dpg.add_drawlist(tag="path_node_icon", parent="path_node_bar", width=30, height=50)
    dpg.draw_rectangle(parent="path_node_icon", pmin=(0, 0), pmax=(25, 25), fill=(229, 194, 152),
                       color=(0, 0, 0), tag="path_brush_rec", thickness=2)
    dpg.add_text("Path brush", parent="path_node_bar")
    dpg.add_spacer(height=10, parent="brushes_menu")

    c = circuitOperations.Circuit([], [], [])
    circuit_image = interfaceObjects.CircuitImage(c)
    caretaker = circuitOperations.UndoRedoCaretaker(c)

    with dpg.item_handler_registry(tag="entry_brush_handler") as handler:
        dpg.add_item_clicked_handler(callback=brush_pick, user_data="entry")

    with dpg.item_handler_registry(tag="exit_brush_handler") as handler:
        dpg.add_item_clicked_handler(callback=brush_pick, user_data="exit")

    with dpg.item_handler_registry(tag="repo_brush_handler") as handler:
        dpg.add_item_clicked_handler(callback=brush_pick, user_data="repo")

    with dpg.item_handler_registry(tag="path_brush_handler") as handler:
        dpg.add_item_clicked_handler(callback=brush_pick, user_data="path")

    dpg.bind_item_handler_registry("exit_node_bar", "exit_brush_handler")
    dpg.bind_item_handler_registry("entry_node_bar", "entry_brush_handler")
    dpg.bind_item_handler_registry("repo_node_bar", "repo_brush_handler")
    dpg.bind_item_handler_registry("path_node_bar", "path_brush_handler")

    with dpg.handler_registry():
        dpg.add_mouse_move_handler(callback=brush_hover, tag="cursor_move")

    dpg.configure_item("plot_handler", callback=plot_click)

    dpg.add_group(tag="action_buttons", parent="control")
    dpg.add_group(parent="action_buttons", tag="undo_redo", horizontal=True)
    dpg.add_button(label="Undo", width=95, height=30,
                   callback=undo_callback, tag="undo_action_button",
                   parent="undo_redo")
    dpg.add_button(label="Redo", width=95, height=30,
                   callback=redo_callback, tag="redo_action_button",
                   parent="undo_redo")
    dpg.add_spacer(height=5, parent="action_buttons")
    dpg.add_button(label="Start process", width=200, height=30,
                   callback=initiate_process, tag="start_process_button",
                   parent="action_buttons", before="wipe_paths_button", show=False)
    dpg.add_button(label="Start sim", width=200, height=30,
                   callback=initiate_sim, tag="start_sim_button",
                   parent="action_buttons", before="wipe_paths_button", show=False)
    dpg.add_spacer(height=5, parent="action_buttons")
    dpg.add_button(label="Exit", width=200, height=30, parent="action_buttons",
                   tag="exit_draw_mode", callback=exit_draw_mode)

def redo_callback():
    # Execute redo and refresh circuit image
    circuit_image.hide_paths()
    circuit_image.hide_nodes()
    caretaker.redo()
    circuit_image.show_nodes()
    circuit_image.show_paths()

    check_initiable()

def undo_callback():
    # Execute undo and refresh circuit image
    circuit_image.hide_paths()
    circuit_image.hide_nodes()
    caretaker.undo()
    circuit_image.show_nodes()
    circuit_image.show_paths()

    check_initiable()

def plot_click(sender, app_data):
    global current_brush, c
    mouse_pos = dpg.get_plot_mouse_pos()
    pos = (round(mouse_pos[0]), round(mouse_pos[1]))

    if app_data[0] == 0:
        if current_brush == "path":
            # Check clicked pos is not exit node
            for n in c.exit_nodes:
                if n.pos == pos:
                    break
            else:
                # If not exit node, then enter path draw
                enter_path_draw(pos)
        elif c.in_node(pos) or c.in_repo(pos):
            for node in c.entry_nodes + c.repos + c.exit_nodes:
                if pos == node.pos:
                    enter_edit(node)
                    # Create and add a restore command for current node state to undo stack
                    new_command = circuitOperations.RestoreNodeCommand(node)
                    caretaker.new_undo_push(new_command)
                    break
        elif True:
            if pos[1] < 26:
                match current_brush:
                    case "entry":
                        new_entry = circuitOperations.Node(pos, 1.00)
                        # Add node delete command for node to undo stack
                        undo_command = circuitOperations.DeleteNodeCommand(new_entry)
                        caretaker.new_undo_push(undo_command)
                        # Add new node to circuit
                        c.add_node(new_entry)
                        # Draw new node
                        dpg.draw_rectangle(pmin=pos, pmax=pos, parent="main_grid",
                                           color=(233, 240, 50), tag=f"node_{pos}")
                        dpg.draw_text((pos[0] - 0.5, pos[1] + 0.5), "1.00", parent="main_grid",
                                      tag=f"node_text_{pos}", size=0.35, color=(0, 0, 0))
                        # Enter edit mode for node
                        enter_edit(new_entry)

                    case "exit":
                        new_exit = circuitOperations.Node(pos, -1.00)
                        # Add node delete command for node to undo stack
                        undo_command = circuitOperations.DeleteNodeCommand(new_exit)
                        caretaker.new_undo_push(undo_command)
                        # Add new node to circuit
                        c.add_node(new_exit)
                        # Draw new node
                        dpg.draw_rectangle(pmin=pos, pmax=pos, parent="main_grid",
                                           color=(23, 240, 250), tag=f"node_{pos}")
                        dpg.draw_text((pos[0] - 0.5, pos[1] + 0.5), "1.00", parent="main_grid",
                                      tag=f"node_text_{pos}", size=0.35, color=(0, 1, 0))
                        # Enter edit mode for node
                        enter_edit(new_exit)

                    case "repo":
                        new_repo = circuitOperations.Repository(pos, 100)
                        # Add node delete command for node to undo stack
                        undo_command = circuitOperations.DeleteNodeCommand(new_repo)
                        caretaker.new_undo_push(undo_command)
                        # Add new node to circuit
                        c.add_repo(new_repo)
                        # Draw new node
                        dpg.draw_rectangle(pmin=pos, pmax=pos, parent="main_grid",
                                           color=(233, 12, 50), tag=f"repo_{pos}")
                        dpg.draw_text(pos, "0", parent="main_grid", tag=f"repo_text_{pos}", size=0.5, color=(0, 250, 250))
                        # Enter edit mode for node
                        enter_edit(new_repo)
    else:
        print()
        print(f"path_space: {c.path_space[pos]}")
        print(f"orientation: {c.path_orientation[pos]}")
        if pos in c.undercurrent_space:
            print(f"undercurrent_space: {c.undercurrent_space[pos]}")

    # If circuit is valid to run, allow 'Start process' button to show
    check_initiable()




def path_click(sender, app_data, user_data):
    global saved_hover_pos
    #user_data is pos from which path would start if executed. saved_hover_pos is end pos of path that has been selected

    if saved_hover_pos[0] >= user_data[0] and saved_hover_pos != user_data:
        if c.in_repo(saved_hover_pos) or c.in_node(saved_hover_pos) or c.path_space[saved_hover_pos] != []:
            new_command = circuitOperations.PathsRestoreCommand(c)
            path_executed = c.path_find(user_data, saved_hover_pos)
            if path_executed:
                caretaker.new_undo_push(new_command)
                circuit_image.hide_paths()
                circuit_image.show_paths()
                exit_path_draw()
            else:
                pass

    # If circuit is valid to run, allow 'Start process' button to show
    check_initiable()

def brush_hover():
    if dpg.is_item_hovered("control"):
        for brush in ["repo", "exit", "entry", "path"]:
            if dpg.is_item_hovered(f"{brush}_node_bar"):
                dpg.configure_item(f"{brush}_brush_rec", color=(200, 75, 200))
            else:
                dpg.configure_item(f"{brush}_brush_rec", color=(0, 0, 0))

def check_initiable():
    for n in c.entry_nodes + c.repos:
        if not c.path_space[n.pos]:
            dpg.configure_item("start_process_button", show=False)
            dpg.configure_item("start_sim_button", show=False)
            break
    else:
        for pos in c.path_space:
            for a in c.path_space[pos]:
                if not c.path_space[a] and not c.in_exit_node(a):
                    dpg.configure_item("start_process_button", show=False)
                    dpg.configure_item("start_sim_button", show=False)
                    break
                else:
                    dpg.configure_item("start_sim_button", show=True)
                    dpg.configure_item("start_process_button", show=True)

def initiate_sim():
    dpg.configure_item("brushes_menu", show=False)
    dpg.configure_item("action_buttons", show=False)

    tcd = circuitOperations.TasepCircuitDispatcher()
    # Storing hidden groups so that tcd knows what to return to
    tcd.hidden = ["brushes_menu", "action_buttons"]
    tcd.circuit = c
    tcd.run_tasep()

    tracked = []
    for n in c.entry_nodes + c.body:
        if n.track:
            tracked.append(n)
    data = circuitOperations.DataRecorder(tracked)
    for node in tracked:
        count = floor(node.check_in[0])
        top = floor(node.check_in[-1])
        if top != count:
            for i, t in enumerate(node.check_in):
                f = floor(t)
                while count != f:
                    count += 1
                    data.currents_1[node.pos].append(0)
                else:
                    if count != top:
                        data.currents_1[node.pos][-1] += 1
            print(sum(data.currents_1[node.pos])/len(data.currents_1[node.pos]))
        node.check_in = []

    data.calc_currents()
    print("Done")
    dpg.configure_item("main_grid", show=False)
    graphs = interfaceObjects.StatisticalFrames(data)
    graphs.setup_frames()


def grid_hover(sender, app_data, user_data):
    global saved_hover_pos, c

    if dpg.is_item_hovered("main_grid"):
        cursor_pos = dpg.get_plot_mouse_pos()
        curr_pos = (round(cursor_pos[0]), round(cursor_pos[1]))
        if curr_pos != saved_hover_pos:
            dpg.delete_item("ind_rec")
            saved_hover_pos = curr_pos


            # Decision sequence for hover indicator (valid path or not)
            if curr_pos[0] < user_data[0] or curr_pos == user_data:
                dpg.draw_rectangle(pmin=curr_pos, pmax=curr_pos, parent="main_grid",
                                   tag="ind_rec", color=(215, 0, 0))
            elif not c.in_repo(curr_pos) and not c.in_node(curr_pos) and c.path_space[curr_pos] == []:
                dpg.draw_rectangle(pmin=curr_pos, pmax=curr_pos, parent="main_grid",
                                   tag="ind_rec", color=(215, 0, 0))
            elif not c.path_find(user_data, curr_pos, hovering=True):
                dpg.draw_rectangle(pmin=curr_pos, pmax=curr_pos, parent="main_grid",
                                   tag="ind_rec", color=(215, 0, 0))
            else:
                dpg.draw_rectangle(pmin=curr_pos, pmax=curr_pos, parent="main_grid",
                                   tag="ind_rec", color=(0, 215, 0))




def brush_pick(sender, app_data, user_data):
    global current_brush

    if user_data != current_brush:
        dpg.add_spacer(width=20, parent="path_node_bar", before=f"{user_data}_node_icon", tag=f"chosen_{user_data}")
        dpg.delete_item(f"chosen_{current_brush}")
        dpg.hide_item("repo_brush_handler")
        current_brush = user_data


def exit_draw_mode():
    global circuit_image

    dpg.delete_item("action_buttons")
    dpg.delete_item("brushes_menu")

    dpg.delete_item("cursor_move")
    for brush in ["repo", "exit", "entry", "path"]:
        dpg.delete_item(f"{brush}_brush_handler")

    # Remove hover/click handlers for drawing
    dpg.delete_item("cursor_move")

    # Wipe drawn circuit
    circuit_image.hide_paths()
    # circuit_image.hide_nodess() CHANGE THIS SOME TIME
    for n in c.exit_nodes + c.entry_nodes:
        dpg.delete_item(f"node_{n.pos}")
        dpg.delete_item(f"node_text_{n.pos}")
    for n in c.repos:
        dpg.delete_item(f"repo_{n.pos}")
        dpg.delete_item(f"repo_text_{n.pos}")

    dpg.add_button(label="Draw circuit", width=200, height=30,
                                 callback=draw_mode, tag="draw_circuit_button", parent="control")
    dpg.add_button(label="Generate circuit", width=200, height=30,
                   callback=genCallbacks.gen_circuit, tag="gen_circuit_button", parent="control")


def enter_edit(node):
    # Hide existing menu
    dpg.configure_item("brushes_menu", show=False)
    dpg.configure_item("action_buttons", show=False)

    # Freeze click handler
    dpg.configure_item("plot_handler", show=False)
    dpg.draw_rectangle(pmin=(-0.5, -0.5), pmax=(49.5,25.5), parent="main_grid",
                       fill=(200, 200, 250, 60), tag="frozen_handler_rec", thickness=0)

    # Render node-edit menu
    dpg.add_group(tag="node_edit_group", parent="control")
    dpg.add_spacer(parent="node_edit_group", height=20)
    # TODO: checkbox for showing currents
    dpg.add_checkbox(label="Track stats", parent="node_edit_group", callback=track_toggle, user_data=node,
                     default_value=node.track)
    dpg.add_spacer(parent="node_edit_group", height=5)
    if node.name == "node":
        dpg.add_group(parent="node_edit_group", horizontal=True, tag="node_edit_slider")
        dpg.add_text("Rate", parent="node_edit_slider")
        dpg.add_spacer(parent="node_edit_slider", width=5)
        dpg.add_spacer(parent="node_edit_group", height=20)
        dpg.add_slider_float(parent="node_edit_slider", width=150, min_value=0.01, max_value=1, clamped=True,
                           callback=rate_adjust, default_value=abs(node.rate), tag="rate_slider",user_data=node)
    elif node.name == "repo":
        dpg.add_text("Choose colour", parent="node_edit_group")
        dpg.add_color_picker(parent="node_edit_group", callback=colour_adjust, default_value=node.colour, user_data=node)
        dpg.add_spacer(parent="node_edit_group", height=5)
    dpg.add_button(label="Delete", width=200, height=30,
                   callback=node_delete, tag="node_delete", parent="node_edit_group", user_data=node)
    dpg.add_button(label="Back", width=200, height=30,
                   callback=exit_edit, tag="node_edit_back", parent="node_edit_group")

def track_toggle(sender, app_data, user_data):
    node = user_data
    node.track = not node.track

def enter_path_draw(pos):
    global saved_hover_pos
    saved_hover_pos = pos
    dpg.draw_rectangle(pmin=pos, pmax=pos, parent="main_grid",
                       tag="ind_rec", color=(215, 0, 0))

    # Hide existing menu
    dpg.configure_item("brushes_menu", show=False)
    dpg.configure_item("action_buttons", show=False)

    # change plot click and hover handler to deal with drawing paths
    dpg.draw_rectangle(pmin=(-0.5, -0.5), pmax=(49.5, 25.5), parent="main_grid",
                       fill=(255, 215, 0, 50), tag="active_brush_rec", thickness=0)
    dpg.draw_rectangle(pmin=(pos[0]-0.65, pos[1]-0.65), pmax=(pos[0]+0.65, pos[1]+0.65), parent="main_grid",
                       fill=(0, 0, 0, 0), tag="start_pos_rec", thickness=0.3, color=(0, 0, 0, 80))
    dpg.configure_item("plot_handler", callback=path_click, user_data=pos)
    dpg.configure_item("cursor_move", callback=grid_hover, user_data=pos)

    # Render node-edit menu
    dpg.add_group(tag="path_draw_group", parent="control")
    dpg.add_text("You cannot draw paths to\nblank spaces on the grid."
                 , parent="path_draw_group", indent=5)
    dpg.add_spacer(parent="path_draw_group", height=10)
    dpg.add_text("Paths cannot go left to\nright."
                 , parent="path_draw_group", indent=5)
    dpg.add_spacer(parent="path_draw_group", height=10)
    dpg.add_button(label="Back", width=200, height=30,
                   callback=exit_path_draw, tag="path_draw_exit", parent="path_draw_group")

def exit_path_draw():
    dpg.delete_item("path_draw_group")
    dpg.delete_item("ind_rec")

    # Change back click handler
    dpg.delete_item("active_brush_rec")
    dpg.delete_item("start_pos_rec")
    dpg.configure_item("plot_handler", callback=plot_click, user_data=None)
    dpg.configure_item("cursor_move", callback=brush_hover, user_data=None)

    # Show brush menu
    dpg.configure_item("brushes_menu", show=True)
    dpg.configure_item("action_buttons", show=True)


def exit_edit():
    dpg.delete_item("node_edit_group")

    # Unfreeze click handler
    dpg.configure_item("plot_handler", show=True)
    dpg.delete_item("frozen_handler_rec")

    dpg.configure_item("brushes_menu", show=True)
    dpg.configure_item("action_buttons", show=True)

def rate_adjust(sender, app_data, user_data):
    # New rate
    new_rate = dpg.get_value(sender)
    # Change rate
    user_data.rate = (user_data.rate*new_rate)/abs(user_data.rate)
    dpg.configure_item(f"node_text_{user_data.pos}", text=str(round(new_rate, 3)))

def colour_adjust(sender, app_data, user_data):
    new_colour = dpg.get_value(sender)
    user_data.colour = new_colour
    dpg.configure_item(f"repo_{user_data.pos}", color=new_colour)



def node_delete(sender, app_data, user_data):
    global c

    # 'user_data' is node to be deleted
    if user_data.name == "repo":
        c.delete_repo(user_data)
        # Remove repo from plot
        dpg.delete_item(f"repo_{user_data.pos}")
        dpg.delete_item(f"repo_text_{user_data.pos}")
    else:
        c.delete_node(user_data)
        # Remove node from plot
        dpg.delete_item(f"node_{user_data.pos}")
        dpg.delete_item(f"node_text_{user_data.pos}")
    circuit_image.hide_paths()
    circuit_image.show_paths()
    # Add create command for node to undo stack
    new_command = circuitOperations.CreateNodeCommand(user_data)
    caretaker.new_undo_push(new_command)
    # Exit edit mode
    exit_edit()
    check_initiable()

def initiate_process():
    dpg.configure_item("brushes_menu", show=False)
    dpg.configure_item("action_buttons", show=False)

    tcd = interfaceObjects.TasepCircuitDispatcherGUI()
    # Storing hidden groups so that tcd knows what to return to
    tcd.hidden = ["brushes_menu", "action_buttons"]
    tcd.circuit = c
    tcd.draw_control_menu()
    tcd.start()


