import dearpygui.dearpygui as dpg
import genCallbacks as gcallbacks
import drawCallbacks as dcallbacks

dim_x, dim_y = 1880, 900

dpg.create_context()
dpg.create_viewport(title="tasepC", resizable=False)
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
            draw_button = dpg.add_button(label="Draw circuit", width=200, height=30,
                                        callback=dcallbacks.draw_mode, tag="draw_circuit_button")
            gen_button = dpg.add_button(label="Generate circuit", width=200, height=30,
                                        callback=gcallbacks.gen_circuit, tag="gen_circuit_button")

        with dpg.window(label="Delete Files", modal=True, show=False, tag="help_window",
                        no_title_bar=True, autosize=True):
            dpg.add_text("- Nodes ordered in menu by occurence from left-to-right. As of now, red 'repositories'\n  onl"
                         "y count the number of particles that have passed and are used in generating\n  the random cir"
                         "cuit. Currents are calculated every three seconds, irrespective of the speed\n"
                         "  factor; see below for more information. "
                         )
            dpg.add_spacer(height=5)
            dpg.add_text("- If 'Orange debug particles' checkbox is ticked, every 10th particle is coloured\n"
                         "  orange. Useful for keeping track of individual particles.")
            dpg.add_spacer(height=5)
            dpg.add_text("- The 'speed factor' slider does not control a simple multiplier for the time-intervals\n"
                         "  between ticks of the exhibited process. Instead each particle tries to move after a random"
                         "\n  time interval, sampled from independent exponential distributions of rate 'speed_factor'."
                         "\n  https://en.wikipedia.org/wiki/Exponential_distribution for more on exponential\n"
                         "  distributions."
                         )
            dpg.add_spacer(height=5)
            dpg.add_text("- For each node, the individual times at which the last 10 particles 'hopped'\n"
                         "  into it are logged. Then\n\n"
                         "              Current = 10/(current_time - tenth_p_time)\n\n"
                         "  where tenth_p_time is the time at which the tenth-last particle hopped into the node.\n"
                         "  When a new particle hops into the node, the list is updated, the 'tenth_p_time' is now\n"
                         "  what was previously the time for the ninth-last particle. I'm not entirely comfortable\n"
                         "  with this method to be quite honest. There perhaps will be a lack of regularity for\n"
                         "  the mixing times of the different nodes (current-wise).")
            dpg.add_spacer(height=5)
            dpg.add_text("- Any suggested improvements please email to DePradaVill@proton.me")
            dpg.add_spacer(height=15)
            dpg.add_button(label="Close", width=75, callback=lambda: dpg.configure_item("help_window", show=False))



            # series belong to a y axi
dpg.setup_dearpygui()
dpg.show_viewport()

dpg.set_primary_window("primary_window", True)

dpg.start_dearpygui()
dpg.destroy_context()
