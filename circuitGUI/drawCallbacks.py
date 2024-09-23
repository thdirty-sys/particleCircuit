import dearpygui.dearpygui as dpg
import circuitOperations
import threading
import genCallbacks

global current_brush
path_rec_count = 0
sep_line_count = 0


class RepeatTimer(threading.Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)


def draw_mode():
    global current_brush, c
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

    tcd_draw = circuitOperations.TasepCircuitDispatcherGUI()
    c = circuitOperations.Circuit([], [], [])

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
        dpg.add_mouse_move_handler(callback=cursor_move, tag="cursor_move")

    dpg.add_item_handler_registry(tag="plot_register")
    dpg.add_item_clicked_handler(callback=plot_click, parent="plot_register", tag="plot_handler")
    dpg.bind_item_handler_registry("main_grid", "plot_register")

    dpg.add_button(label="Exit", width=200, height=30, parent="control",
                   tag="exit_draw_mode", callback=exit_draw_mode)


def plot_click():
    global current_brush, c
    mouse_pos = dpg.get_plot_mouse_pos()
    pos = (round(mouse_pos[0]), round(mouse_pos[1]))

    if current_brush == "path":
        pass
    elif c.in_node(pos) or c.in_repo(pos):
        for node in c.entry_nodes + c.repos + c.exit_nodes:
            if pos == node.pos:
                enter_edit(node)
    elif True:
        match current_brush:
            case "entry":
                new_entry = circuitOperations.Node(pos, 0.01)
                c.entry_nodes.append(new_entry)
                dpg.draw_rectangle(pmin=pos, pmax=pos, parent="main_grid",
                                   color=(233, 240, 50), tag=f"node_{pos}")
                dpg.draw_text((pos[0] - 0.5, pos[1] + 0.5), "0.01", parent="main_grid",
                              tag=f"node_text_{pos}", size=0.35, color=(0, 0, 0))
                enter_edit(new_entry)

            case "exit":
                new_exit = circuitOperations.Node(pos, -0.01)
                c.exit_nodes.append(new_exit)
                dpg.draw_rectangle(pmin=pos, pmax=pos, parent="main_grid",
                                   color=(23, 240, 250), tag=f"node_{pos}")
                dpg.draw_text((pos[0] - 0.5, pos[1] + 0.5), "0.01", parent="main_grid",
                              tag=f"node_text_{pos}", size=0.35, color=(0, 1, 0))
                enter_edit(new_exit)

            case "repo":
                new_repo = circuitOperations.Repository(pos, 100)
                c.repos.append(new_repo)
                dpg.draw_rectangle(pmin=pos, pmax=pos, parent="main_grid",
                                   color=(233, 12, 50), tag=f"repo_{pos}")
                dpg.draw_text(pos, 0, parent="main_grid", tag=f"repo_text_{pos}", size=0.5, color=(0, 250, 250))
                enter_edit(new_repo)


def cursor_move():
    if dpg.is_item_hovered("control"):
        for brush in ["repo", "exit", "entry", "path"]:
            if dpg.is_item_hovered(f"{brush}_node_bar"):
                dpg.configure_item(f"{brush}_brush_rec", color=(200, 75, 200))
            else:
                dpg.configure_item(f"{brush}_brush_rec", color=(0, 0, 0))


def brush_pick(sender, app_data, user_data):
    global current_brush

    if user_data != current_brush:
        dpg.add_spacer(width=20, parent="path_node_bar", before=f"{user_data}_node_icon", tag=f"chosen_{user_data}")
        dpg.delete_item(f"chosen_{current_brush}")
        dpg.hide_item("repo_brush_handler")
        current_brush = user_data


def exit_draw_mode():
    dpg.delete_item("exit_draw_mode")
    dpg.delete_item("brushes_menu")

    dpg.delete_item("cursor_move")
    for brush in ["repo", "exit", "entry", "path"]:
        dpg.delete_item(f"{brush}_brush_handler")

    dpg.add_button(label="Draw circuit", width=200, height=30,
                                 callback=draw_mode, tag="draw_circuit_button", parent="control")
    dpg.add_button(label="Generate circuit", width=200, height=30,
                                callback=genCallbacks.gen_circuit, tag="gen_circuit_button", parent="control")


def enter_edit(node):
    # Hide existing menu
    dpg.configure_item("brushes_menu", show=False)
    dpg.configure_item("exit_draw_mode", show=False)

    # Freeze click handler
    dpg.configure_item("plot_handler", show=False)
    dpg.draw_rectangle(pmin=(-0.5, -0.5), pmax=(49.5,25.5), parent="main_grid",
                       fill=(200, 200, 250, 60), tag="frozen_handler_rec", thickness=0)

    # Render node-edit menu
    dpg.add_group(tag="node_edit_group", parent="control")
    dpg.add_button(label="Delete", width=200, height=30,
                   callback=node_delete, tag="node_delete", parent="node_edit_group", user_data=node)
    dpg.add_button(label="Back", width=200, height=30,
                   callback=exit_edit, tag="node_edit_back", parent="node_edit_group")
    if node.name == "node":
        pass

def exit_edit():
    dpg.delete_item("node_edit_group")

    # Unfreeze click handler
    dpg.configure_item("plot_handler", show=True)
    dpg.delete_item("frozen_handler_rec")

    dpg.configure_item("brushes_menu", show=True)
    dpg.configure_item("exit_draw_mode", show=True)


def node_delete(sender, app_data, user_data):
    global c

    # 'user_data' is node to be deleted
    if user_data.name == "repo":
        c.repos.remove(user_data)
        # Remove repo from plot
        dpg.delete_item(f"repo_{user_data.pos}")
        dpg.delete_item(f"repo_text_{user_data.pos}")
    else:
        if user_data.rate < 0:
            c.exit_nodes.remove(user_data)
        else:
            c.entry_nodes.remove(user_data)
        # Remove node from plot
        dpg.delete_item(f"node_{user_data.pos}")
        dpg.delete_item(f"node_text_{user_data.pos}")
    exit_edit()

    print(c.body)


