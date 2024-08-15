import dearpygui.dearpygui as dpg
import environCallbacks as callbacks

dim_x, dim_y = 1880, 900

dpg.create_context()
dpg.create_viewport(title="Particle Circuit", resizable=False)
dpg.configure_viewport(0, x_pos=0, y_pos=0, width=dim_x, height=dim_y)

with dpg.window(tag="primary_window"):
    with dpg.group(horizontal=True):
        with dpg.plot(no_menus=False, no_title=True, no_box_select=True, no_mouse_pos=True, width=1625,
                              height=845, equal_aspects=True, tag="main_grid"):

            #create x and y axes; arguments to make it as unidentifiable as a graph
            def_x = dpg.add_plot_axis(axis=0, no_tick_marks=True, no_tick_labels=True, lock_min=True, no_gridlines=True)
            def_y = dpg.add_plot_axis(axis=1, no_tick_marks=True, no_tick_labels=True, lock_min=True, no_gridlines=True)

            dpg.set_axis_limits(axis=def_x, ymin=-0.5, ymax=49.5)
            dpg.set_axis_limits(axis=def_y, ymin=-0.5, ymax=25.5)



            #add horizontal bars and vertical bars
            dpg.add_vline_series(x=[n-1.5 for n in range(51)], parent=def_x)
            dpg.add_hline_series(x=[f-1.5 for f in range(27)], parent=def_y)



        with dpg.child_window(tag="control", border=True):
            gen_button = dpg.add_button(label="Generate circuit", width=200, height=30,
                                        callback=callbacks.gen_circuit, tag="gen_circuit_button")

        with dpg.window(label="Delete Files", modal=True, show=False, tag="help_window", no_title_bar=True):
            dpg.add_text("All those beautiful files will be deleted.\nThis operation cannot be undone!")
            dpg.add_button(label="OK", width=75, callback=lambda: dpg.configure_item("modal_id", show=False))



            # series belong to a y axi
dpg.setup_dearpygui()
dpg.show_viewport()

dpg.set_primary_window("primary_window", True)

dpg.start_dearpygui()
dpg.destroy_context()
