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
    global current_brush
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
    blank_circuit = circuitOperations.Circuit([], [], [])

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
    dpg.add_item_clicked_handler(callback=plot_click, parent="plot_register")
    dpg.bind_item_handler_registry("main_grid", "plot_register")

    dpg.add_button(label="Exit", width=200, height=30, parent="control",
                   tag="exit_draw_mode", callback=exit_draw_mode)


def plot_click():
    global current_brush
    mouse_pos = dpg.get_plot_mouse_pos()

    match current_brush:
        case "entry":
            print(mouse_pos)

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

    draw_button = dpg.add_button(label="Draw circuit", width=200, height=30,
                                 callback=draw_mode, tag="draw_circuit_button", parent="control")
    gen_button = dpg.add_button(label="Generate circuit", width=200, height=30,
                                callback=genCallbacks.gen_circuit, tag="gen_circuit_button", parent="control")



