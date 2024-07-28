import dearpygui.dearpygui as dpg
import environCallbacks as callbacks


dpg.create_context()
dpg.create_viewport(title="Particle Circuit")
dpg.configure_viewport(0, x_pos=0, y_pos=0, width=1920, height=900)

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

            """dpg.draw_polyline(points=[[0,0],[4,0],[4,5]], thickness=1, color=[220, 220, 220])
            dpg.draw_circle(center=[1,0], radius=0.35, color=[0,0,0], fill=[0,0,0], segments=120)"""



        with dpg.child_window(tag="control", border=True):
            gen_button = dpg.add_button(label="Generate circuit", width=150, height=20,
                                        callback=callbacks.gen_circuit, tag="gen_circuit_button")



            # series belong to a y axi
dpg.setup_dearpygui()
dpg.show_viewport()

dpg.set_primary_window("primary_window", True)

dpg.start_dearpygui()
dpg.destroy_context()
