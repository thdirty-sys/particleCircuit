import dearpygui.dearpygui as dpg
import circuitGUI as GUI
from screeninfo import get_monitors

def screen_dim():
    for m in get_monitors():
        if m.is_primary:
            return m.width, m.height

def nothing():
    pass



def create_application():
    dpg.create_context()
    dpg.create_viewport(title="tasepC", resizable=False, large_icon="tasepC.ico", small_icon="tasepC.ico")
    dpg.set_viewport_clear_color([0, 0, 0])
    dpg.configure_viewport(0, x_pos=0, y_pos=0, width=GUI.dim_x, height=GUI.dim_y)

    with dpg.window(tag="primary_window"):
        with dpg.group(horizontal=True):
            with dpg.plot(no_menus=False, no_title=True, no_box_select=True, no_mouse_pos=False,
                          width=GUI.circuit_space_x, height=GUI.circuit_space_y, equal_aspects=True, tag="main_grid"):

                #create x and y axes; arguments to make it as unidentifiable as a graph
                def_x = dpg.add_plot_axis(dpg.mvXAxis, no_tick_marks=True, no_tick_labels=True, lock_min=True,
                                          tag="x_axis", no_gridlines=True)
                def_y = dpg.add_plot_axis(dpg.mvYAxis, no_tick_marks=True, no_tick_labels=True, lock_min=True,
                                          tag="y_axis", no_gridlines=True)

                dpg.set_axis_limits(axis=def_x, ymin=-0.5, ymax=49.5)
                dpg.set_axis_limits(axis=def_y, ymin=-0.5, ymax=25.5)

                #add horizontal bars and vertical bars
                dpg.add_inf_line_series(x=[n - 1.5 for n in range(51)], parent=def_x)
                dpg.add_inf_line_series(x=[f - 1.5 for f in range(27)], parent=def_y, horizontal=True)


            with dpg.child_window(tag="control", border=True):
                draw_button = dpg.add_button(label="Draw circuit", width=-1, height=30,
                                            callback=GUI.drawCallbacks.draw_mode, tag="draw_circuit_button")
                gen_button = dpg.add_button(label="Generate circuit", width=-1, height=30,
                                            callback=GUI.genCallbacks.gen_circuit, tag="gen_circuit_button")

            with dpg.window(label="Delete Files", modal=True, show=False, tag="help_window",
                            no_title_bar=True, autosize=True):
                dpg.add_text("- Nodes ordered in menu by occurence from left-to-right. As of now, red 'repositories'\n  onl"
                             "y count the number of particles that have passed."
                             )
                dpg.add_spacer(height=5)
                dpg.add_text("- If 'Orange debug particles' checkbox is ticked, every 10th particle is coloured\n"
                             "  orange. Useful for keeping track of individual particles.")
                dpg.add_spacer(height=5)
                dpg.add_text("- The 'speed factor' slider does not control a simple multiplier for the time-intervals\n"
                             "  between ticks of the exhibited process. Instead each particle tries to move after a random"
                             "\n  time interval, sampled from independent exponential distributions of rate 'speed_factor'."
                             )
                dpg.add_spacer(height=5)
                dpg.add_text("- Currents are calculated using the system's internal clock.\n\n"
                             "              Current = # particles hopped into node/interval size\n\n"
                             "  Once the system arrives at its non-equilibrium steady state, stationarity\n"
                             "  requires that the average current is constant along any connected stretch.\n"
                             "  As we vary entry and exit rates TASEP exhibits a complex profile\n"
                             "  of phases, for such a simple process, even at finite length scales.\n"
                             "  The phase transitions are well studied. Below are some relevant papers:")
                dpg.add_spacer(height=5)
                dpg.add_text("Schütz, G. M., & Domany, E. (1993).\n"
                             "'Phase Transitions in an Exactly Soluble One-Dimensional Exclusion Process'\n"
                             "Journal of Statistical Physics, 72(1-2), 277–296.\n\n"
                             " Derrida, B., Evans, M. R., Hakim, V., & Pasquier, V. (1993).\n"
                             "'Exact Solution of a 1D Asymmetric Exclusion Model Using a Matrix Formulation'\n"
                             "Journal of Physics A: Mathematical and General, 26(7), 1493.\n\n"
                             " de Gier, J., & Essler, F. H. L. (2006).\n"
                             "'Dynamical Transition in the Open-Boundary Totally Asymmetric Exclusion Process'\n"
                             "Physical Review Letters, 95(24), 240601.")
                dpg.add_spacer(height=5)
                dpg.add_text("- Any suggested improvements please email to DePradaVill@proton.me")
                dpg.add_spacer(height=15)
                dpg.add_button(label="Close", width=75, callback=lambda: dpg.configure_item("help_window", show=False))

            with dpg.item_handler_registry(tag="plot_register") as handler:
                dpg.add_item_clicked_handler(callback=nothing, tag="plot_handler")
            dpg.bind_item_handler_registry("main_grid", "plot_register")

                # series belong to a y axi
    dpg.setup_dearpygui()
    dpg.show_viewport()

    dpg.set_primary_window("primary_window", True)

    dpg.start_dearpygui()
    dpg.destroy_context()

def set_dimensions(screen_width):
    if screen_width <= 1880:
        GUI.dim_x = 1210
        GUI.dim_y = 565
        GUI.circuit_space_x = 975
        GUI.circuit_space_y = 510
        GUI.plot_x = 800
        GUI.plot_y = 400




if __name__ == '__main__':
    x, y = screen_dim()
    set_dimensions(x)
    create_application()
