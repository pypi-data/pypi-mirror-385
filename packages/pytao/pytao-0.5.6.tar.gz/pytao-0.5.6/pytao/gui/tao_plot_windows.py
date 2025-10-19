"""
Provides windows for viewing and editing plots in tao
"""

import tkinter as tk
from tkinter import messagebox, ttk

from matplotlib.backend_bases import key_press_handler
from matplotlib.backends._backend_tk import FigureManagerTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from ..util.parameters import str_to_tao_param, tao_parameter_dict
from .tao_base_windows import (
    Tao_Popup,
    Tao_Toplevel,
    ele_shape_frame,
    tabbed_frame,
    tao_message_box,
    tao_scroll_frame,
)
from .tao_ele_location import in_element
from .tao_lat_windows import tao_ele_window
from .tao_mpl_toolbar import taotoolbar
from .tao_set import tao_set
from .tao_widget import tk_tao_parameter
from .taoplot import taoplot

# -----------------------------------------------------
# Plot placing window


class tao_place_plot_window(Tao_Toplevel):
    """
    Allows the user to choose from defined template
    plots and plot them in matplotlib windows
    Currently only supported in matplotlib mode
    """

    def __init__(self, root, pipe, *args, **kwargs):
        self.root = root
        self.tao_id = "plot"
        Tao_Toplevel.__init__(self, root, *args, **kwargs)
        self.title("Choose Plot")
        self.pipe = pipe
        self.grid_rowconfigure(0, weight=1)
        self.list_frame = tk.Frame(self)
        # self.list_frame.pack(side='top', fill='both', expand=1)
        self.list_frame.grid(row=0, column=0, sticky="NSEW")
        self.button_frame = tk.Frame(self)
        self.button_frame.grid(row=1, column=0, sticky="EW")
        self.button_frame.grid_columnconfigure(0, weight=1)
        self.button_frame.grid_columnconfigure(1, weight=1)
        # self.button_frame.pack(side='bottom', fill='x', expand=1)
        self.refresh()
        tk.Button(self.button_frame, text="Edit Template", command=self.edit_template).grid(
            row=0, column=0, sticky="EW"
        )
        tk.Button(self.button_frame, text="Plot!", command=self.plot_cmd).grid(
            row=0, column=1, sticky="EW"
        )

    def refresh(self):
        """
        Responsible for creating widgets and filling them with plots
        """
        for child in self.list_frame.winfo_children():
            child.destroy()

        # List of plots w/descriptions
        plots = self.pipe.cmd_in("python plot_list t")
        plots = plots.splitlines()
        for i in range(len(plots)):
            # get the description
            plot = plots[i].split(";")[1]
            plot_info = self.pipe.cmd_in("python plot1 " + plot)
            plot_info = plot_info.splitlines()
            for line in plot_info:
                if line.find("description;") == 0:
                    d = line.split(";")[3]
                    break
                else:
                    d = ""
            plots[i] = [plot, d]
        widths = [0, 0]  # track column widths

        # Create list
        titles = ["Name", "Description"]
        self.tree = ttk.Treeview(self.list_frame, columns=titles, show="headings")
        # Column titles
        for title in titles:
            self.tree.heading(title, text=title)
            self.tree.column(title, stretch=True, anchor="w")

        # Fill rows
        for plot in plots:
            self.tree.insert("", "end", values=plot)
            for j in range(len(plot)):
                if len(plot[j]) * 10 > widths[j]:
                    widths[j] = len(plot[j]) * 10

        # Set column widths appropriately
        for j in range(len(titles)):
            if len(titles[j]) * 10 > widths[j]:
                widths[j] = len(titles[j]) * 10
            self.tree.column(titles[j], width=widths[j], minwidth=widths[j])

        # Scrollbars
        vbar = ttk.Scrollbar(self.list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vbar.set)

        vbar.pack(side="right", fill="y", expand=0)
        self.tree.pack(side="left", fill="both", expand=1)
        self.widths = widths

        # Double click to open plot
        self.tree.bind("<Double-Button-1>", self.plot_cmd)
        # Single click to set self.plot
        self.tree.bind("<Button-1>", self.set_plot)

        tot = 0
        for w in widths:
            tot = tot + w
        self.maxsize(1800, 1000)
        self.minsize(tot, 100)

    def plot_cmd(self, event=None):
        if self.root.plot_mode == "matplotlib":
            self.mpl_plot(event)
        elif self.root.plot_mode == "pgplot/plplot":
            self.pg_plot(event)

    def mpl_plot(self, event=None):
        """
        Creates a new matplotlib window with the currently selected plot
        """
        if self.set_plot():
            messagebox.showwarning("Error", "Please choose a template to plot.", parent=self)
            return
        self.set_plot()
        tao_plot_window(self.root, self.plot, self.pipe)

    def pg_plot(self, event=None):
        """
        Opens a window that asks the user where the plot should be placed,
        and places it on the pgplot page
        """
        if self.set_plot():
            messagebox.showwarning("Error", "Please choose a template to plot.", parent=self)
            return
        self.set_plot()
        tao_pgplot_place_window(self.root, self.plot, self.pipe)

    def set_plot(self, event=None):
        """
        Sets self.plot to the selected plot in the list
        """
        x = self.tree.focus()
        if x == "":
            return 1
        row = self.tree.item(x)
        self.plot = row["values"][0]
        return 0

    def edit_template(self, event=None):
        """
        Opens up a plot editting window and loads the selected template
        """
        if self.set_plot():
            messagebox.showwarning("Error", "Please choose a template to edit.", parent=self)
            return
        tao_new_plot_template_window(self.root, self.pipe, self.plot, "T")


# ----------------------------------------------------
# Matplotlib plotting window


class tao_plot_window(Tao_Toplevel):
    """
    Displays one (perhaps multiple) matplotlib plots that the user has specified from the plotting
    template window that they want to plot. Creating a window in tkinter is necessary rather than using
    matplotlib's built in system for creating windows because using that system will halt the tkinter
    mainloop until the plots are closed.
    If the region to place the graph is not specified, one will be selected automatically.
    """

    def __init__(self, root, template, pipe, region=None, *args, **kwargs):
        if region == "layout":  # do not place plots in the layout region
            return
        if template == "key_table":
            messagebox.showwarning("Warning", "Key table not available in the GUI")
            return
        if root.plot_mode != "matplotlib":
            return  # Should never be called in pgplot mode
        # verify that the graphs for this template are valid
        # must place the template first to get accurate info
        tmp_reg = root.placed.place_template(template)
        plot1 = pipe.cmd_in("python plot1 " + tmp_reg).splitlines()
        valid = True
        for i in range(str_to_tao_param(plot1[0]).value):
            plot_graph = pipe.cmd_in(
                "python plot_graph " + tmp_reg + "." + str_to_tao_param(plot1[i + 1]).value
            ).splitlines()
            if not tao_parameter_dict(plot_graph)["is_valid"].value:
                valid = False
                break
        root.placed.unplace_region(tmp_reg)
        if not valid:
            messagebox.showwarning(
                "Warning",
                "The plot you have selected ("
                + template
                + ") has one or more invalid graphs.",
            )
            return
        self.root = root
        self.tao_id = "plot"
        Tao_Toplevel.__init__(self, root, *args, **kwargs)
        self.template = template  # The template plot being plotted
        self.pipe = pipe
        self.fig = False  # Default value

        self.region = self.root.placed.place_template(self.template, region)

        self.mpl = taoplot(pipe, self.region)
        self.title(template + " (" + self.region + ")")
        self.refresh()

    ## @profile
    def refresh(self, event=None, width=1):
        """
        Makes the call to matplotlib to draw the plot to the window
        """
        # Clear the window
        for child in self.winfo_children():
            child.destroy()

        # Get plotting results
        self.plot_output = self.mpl.plot(width)

        # Get the figure
        self.fig = self.plot_output[0]

        # Get figure information
        self.fig_info = self.plot_output[1]

        # Create widgets to display the figure
        canvas = FigureCanvasTkAgg(self.fig, master=self)
        canvas.draw()
        # canvas.get_tk_widget().pack(side="top", fill="both", expand=1)
        toolbar = taotoolbar(canvas, self, width, self.root.GUI_DIR)
        toolbar.update()
        # DO NOT TOUCH
        canvas.manager = FigureManagerTk(canvas, self.fig.number, tk.Toplevel(self.root))

        # toolbar = taotoolbar(canvas, self)
        # toolbar.update()
        # canvas._tkcanvas.pack(side="top", fill="both", expand=1)

        def on_key_press(event):
            key_press_handler(event, canvas, toolbar)

        canvas.mpl_connect("key_press_event", on_key_press)

        def on_click(event):
            """opens element information window if an element is double clicked on"""
            if event.dblclick:
                eleList = in_element(event.xdata, event.ydata, self.fig_info)
                for i in eleList:
                    tao_ele_window(
                        self.root,
                        self.pipe,
                        default=[self.fig_info[1], i[0], i[1], self.fig_info[3]],
                    )

        canvas.mpl_connect("button_press_event", on_click)

        """
        if self.fig_info[0] == 'floor_plan':
            self.fig.subplots_adjust(bottom=0.2) #adds room below graph for slider
            width_slider = Slider(self.fig.add_axes([.1,.05,.8,.05]), 'width', 0, 2, width) #element width slider

            def update_slider(width):
                self.refresh(width=width_slider.val)

            width_slider.on_changed(update_slider) #call update when slider moves
        """

        self.update_idletasks()
        self.pack_propagate(False)

    def destroy(self):
        # Clear self.region
        self.root.placed.unplace_region(self.region)
        Tao_Toplevel.destroy(self)


class tao_new_plot_template_window(Tao_Toplevel):
    """
    Provides a window for creating new plot templates (and their
    associated graphs and curves)
    default: if present, opens the plot editor with that plot selected
    mode: 'N' for new template, 'T' for editing existing templates, and 'R'
    for editing active plots
    """

    def __init__(self, root, pipe, default=None, mode="N", *args, **kwargs):
        self.root = root
        Tao_Toplevel.__init__(self, root, *args, **kwargs)
        self.pipe = pipe
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)
        self.title("Plot Editor")
        self.name = ""
        self.mode = mode
        self.mode_var = tk.StringVar()
        self.x_axis_type = "index"
        self.handler_block = False
        # Some internal variables defined here:
        self._plot_list = []
        self._plot_display_list = []
        self._index_list = []
        self._region_list = []

        # Frame for inputting plot parameters
        self.plot_frame = tk.Frame(self)
        self.plot_frame.grid(row=1, column=0, sticky="NSEW")

        self.fill_plot_frame()
        # X-axis/graph type compatibility dict
        self.compat_dict = {}
        self.compat_dict["index"] = self.compat_dict["ele_index"] = self.compat_dict[
            "lat"
        ] = self.compat_dict["var"] = self.compat_dict["data"] = ["data"]
        self.compat_dict["index"].append("floor_plan")
        self.compat_dict["s"] = ["data", "lat_layout"]
        self.compat_dict["floor"] = ["floor_plan"]
        self.compat_dict["phase_space"] = [
            "dynamic_aperture",
            "histogram",
            "phase_space",
        ]
        self.compat_dict["histogram"] = ["histogram"]
        self.compat_dict["none"] = ["floor_plan"]  # FIXME
        # Graph frame (includes curve/ele shape frame)
        self.graph_frame = tabbed_frame(self, lambda arg: new_graph_frame(arg, self))
        self.graph_frame.grid(row=1, column=1, sticky="NSEW")
        # Run additional setup for edit (T/R) modes
        if self.mode != "N":
            self.tr_setup(default)

        # Load the default plot
        # if default != None:
        #    self.plot_param_list[0].tk_var.set(default)
        #    self.clone_plot(ask=False)

    def fill_plot_frame(self):
        # tk.Label(self, text="New Plot Template",
        #        font=('Sans', 16, 'bold')).grid(
        #                row=0, column=0, columnspan=2, sticky='EW')
        # Reserve space for template/active plot selectors
        # in T/R mode
        self.plot_frame_offset = 3  # TODO:why 3?
        pfo = self.plot_frame_offset  # alias

        # Small bit of setup
        def my_ttp(x):
            """shorcut for the following commonly used construct"""
            return tk_tao_parameter(str_to_tao_param(x), self.plot_frame, self.pipe)

        # Widgets
        params = [
            "name;STR;T;",
            "description;STR;T;",
            "x_axis_type;ENUM;T;",
            "autoscale_gang_x;LOGIC;T;T",
            "autoscale_gang_y;LOGIC;T;T",
            "autoscale_x;LOGIC;T;F",
            "autoscale_y;LOGIC;T;F",
            "n_curve_pts;INT;T;",
        ]
        self.plot_param_list = list(map(my_ttp, params))

        # Parameter index lookup (for convenience)
        self.ixd = {}  # index dictionary
        for i in range(len(self.plot_param_list)):
            self.ixd[self.plot_param_list[i].param.name] = i

        # Labels
        def plot_label_maker(x):
            """Helper function"""
            return tk.Label(self.plot_frame, text=x)

        labels = [
            "Plot Name:",
            "Description:",
            "X-axis Type:",
            "Autoscale gang X:",
            "Autoscale gang Y:",
            "Autoscale X:",
            "Autoscale Y:",
            "Number of curve points:",
        ]
        self.plot_label_list = list(map(plot_label_maker, labels))

        # Grid widgets and labels
        for i in range(len(self.plot_param_list)):
            self.plot_label_list[i].grid(row=i + pfo, column=0, sticky="W")
            self.plot_param_list[i].tk_wid.grid(row=i + pfo, column=1, sticky="EW")
        i += 1

        # Warning labels
        self.name_warning_1 = tk.Label(self.plot_frame, text="Cannot be empty")
        self.name_warning_2 = tk.Label(self.plot_frame, text="Cannot contain whitespace")

        # Responses to edits
        self.plot_param_list[0].tk_wid.bind("<FocusOut>", self.plot_name_handler)
        self.plot_param_list[self.ixd["x_axis_type"]].tk_var.trace(
            "w", self.x_axis_type_handler
        )

        # Clone existing plot
        existing_plot_templates = self.pipe.cmd_in("python plot_list t").splitlines()
        for i in range(len(existing_plot_templates)):
            existing_plot_templates[i] = existing_plot_templates[i].split(";")[1]
        existing_plot_templates = ["None"] + existing_plot_templates
        self.existing_plot_templates = existing_plot_templates[1:]
        self.clone_plot = tk.StringVar()
        self.clone_plot.set("None")
        self.clone_chooser = ttk.Combobox(
            self.plot_frame,
            textvariable=self.clone_plot,
            values=existing_plot_templates,
            state="readonly",
        )
        self.clone_b = tk.Button(self.plot_frame, text="Clone", command=self.clone_plot_method)

        tk.Label(self.plot_frame, text="Clone existing plot:").grid(
            row=i + pfo, column=0, sticky="W"
        )
        self.clone_chooser.grid(row=i + pfo, column=1, sticky="EW")
        self.clone_b.grid(row=i + pfo, column=2, sticky="W")
        i += 1

        # Frame for control buttons (e.g. create plot button)
        self.control_frame = tk.Frame(self.plot_frame)
        self.control_frame.grid(row=i + pfo, column=0, columnspan=3, sticky="SEW")
        self.plot_frame.grid_rowconfigure(i + pfo, weight=1)
        i += 1

        # Control frame widgets
        self.write_var = tk.StringVar()
        tk.Radiobutton(self.control_frame, variable=self.write_var, value="new").grid(
            row=0, column=0, sticky="W"
        )
        tk.Label(self.control_frame, text="Save as new template").grid(
            row=0, column=1, sticky="W"
        )
        tk.Radiobutton(self.control_frame, variable=self.write_var, value="overwrite").grid(
            row=1, column=0, sticky="W"
        )
        tk.Label(self.control_frame, text="Overwrite existing template:").grid(
            row=1, column=1, sticky="W"
        )
        self.overwrite_var = tk.StringVar()
        self._overwrite_ix = ""
        self.overwrite_var.trace("w", self._overwrite_trace)
        self.overwrite_box = ttk.Combobox(
            self.control_frame,
            textvariable=self.overwrite_var,
            values=existing_plot_templates[1:],
            state="readonly",
        )
        self.overwrite_var.set(existing_plot_templates[1])
        self.overwrite_box.grid(row=1, column=2, sticky="EW")

        if self.mode != "N":
            tk.Radiobutton(self.control_frame, variable=self.write_var, value="self").grid(
                row=2, column=0, sticky="W"
            )
            tk.Label(self.control_frame, text="Save changes to this plot").grid(
                row=2, column=1, sticky="W"
            )
            self.write_var.set("self")
        else:
            self.write_var.set("new")

        self.create_b = tk.Button(
            self.control_frame, text="Create template", command=self.create_template
        )
        self.create_b.grid(row=3, column=0, columnspan=2, sticky="EW")
        self.create_plot_b = tk.Button(
            self.control_frame, text="Create and plot", command=self.create_and_plot
        )
        self.create_plot_b.grid(row=3, column=2, sticky="EW")

        # Focus the name entry
        self.plot_param_list[0].tk_wid.focus_set()

    def tr_setup(self, default):
        """
        Performs additional setup needed in template/region mode,
        i.e. creates drop down lists to select plots,
        and loads in the default plot, or the first plot in the list
        if default == None
        Also adds options to the save box
        """
        # Create template selectors
        self.mode_var.set("Templates" if self.mode == "T" else "Active Plots")
        self.plot_select_label = tk.Label(self.plot_frame, text="Select plot:")
        self.mode_select = tk.OptionMenu(
            self.plot_frame,
            self.mode_var,
            "Templates",
            "Active Plots",
            command=self.swap_mode,
        )
        self.plot_var = tk.StringVar()  # tkinter stringvar for the actual plot name
        self._plot_id = ""  # unique plot identifier e.g. @T1, @R12, as a string
        self.plot_var.trace("w", self._index_trace)
        self.plot_select = tk.ttk.Combobox(
            self.plot_frame, textvariable=self.plot_var, values=[]
        )
        self.plot_select.bind("<<ComboboxSelected>>", self.refresh)
        self.plot_select.bind("<Return>", self.refresh)

        self.plot_select_label.grid(row=0, column=0, sticky="W")
        self.mode_select.grid(row=0, column=1, sticky="EW")
        self.plot_select.grid(row=0, column=2, sticky="EW")

        # Load the default template
        self.swap_mode(overide=True)  # also runs self.refresh()
        # This needs to come after swap_mode so that self._index_list is filled
        if default:
            self.plot_var.set(default)
            self.refresh()

    def swap_mode(self, overide=False, event=None):
        """
        Swaps between showing templates and active plots
        Will always run if overide is set to True
        """
        # Make sure window is not in 'N' mode
        if self.mode == "N":
            return
        # Switch self.mode
        mode_dict = {"Templates": "T", "Active Plots": "R"}
        new_mode = mode_dict[self.mode_var.get()]
        if (self.mode == new_mode) and not overide:
            return  # no action necessary
        self.mode = new_mode

        # Template plots
        t_plot_list = self.pipe.cmd_in("python plot_list t")
        t_plot_list = t_plot_list.splitlines()
        t_index_list = len(t_plot_list) * [0]  # get correct length
        for i in range(len(t_plot_list)):
            t_index_list[i], t_plot_list[i] = t_plot_list[i].split(";")

        # Active plots
        r_plot_list = self.pipe.cmd_in("python plot_list r")
        new_r_plot_list = []
        r_index_list = []
        r_region_list = []  # needed to open the correct graph/curve windows
        r_plot_list = r_plot_list.splitlines()
        for i in range(len(r_plot_list)):
            if r_plot_list[i].split(";")[2] != "":  # region contains a plot
                new_r_plot_list.append(r_plot_list[i].split(";")[2])
                r_index_list.append(r_plot_list[i].split(";")[0])
                r_region_list.append(r_plot_list[i].split(";")[1])
        r_plot_list = new_r_plot_list

        # Populate self.plot_list and self.index_list
        if self.mode == "T":
            self._plot_list = t_plot_list
            self._plot_display_list = t_plot_list
            self._index_list = t_index_list
        elif self.mode == "R":
            self._plot_list = r_plot_list
            self._plot_display_list = []
            self._index_list = r_index_list
            self._region_list = r_region_list
            for i in range(len(self._plot_list)):
                self._plot_display_list.append(
                    self._plot_list[i] + " (" + self._region_list[i] + ")"
                )

        self.plot_select.configure(values=self._plot_display_list)
        if self._plot_list == []:
            self.mode = "N"
            self.plot_select_label.grid_forget()
            self.mode_select.grid_forget()
            self.plot_select.grid_forget()
            return
        if (not overide) or (
            self.plot_var.get() == ""
        ):  # only called with overide on setup -> don't clobber default
            if self.mode == "T":
                self.plot_var.set(self._plot_display_list[0])
            else:
                self.plot_var.set(
                    self._plot_display_list[self._plot_list.index(self.plot_var.get())]
                )
        self.refresh()

    def clone_plot_method(self, ask=True):
        """
        Clone the plot specified by plot_name
        """
        plot_name = self.clone_plot.get()
        clone_graphs = []
        if plot_name == "None":
            return
        ans_var = tk.StringVar()
        # Ask if user wants to keep existing graphs
        if ask:
            tao_message_box(
                self.root,
                self,
                ans_var,
                title="Warning",
                message="Would you like to keep or discard the graphs you defined for "
                + self.name
                + "?",
                choices=["Keep", "Discard"],
            )
        else:
            ans_var.set("Discard")
        if ans_var.get() == "Keep":
            c4 = False
        elif ans_var.get() == "Discard":
            c4 = True
        else:
            return
        # Specified plot to clone
        plot1 = tao_parameter_dict(self.pipe.cmd_in("python plot1 " + plot_name).splitlines())
        num_graphs = plot1["num_graphs"].value
        for i in range(1, num_graphs + 1):
            clone_graphs.append(plot1["graph[" + str(i) + "]"].value)
        # Ask what to do about plot properties
        use_plot_props = plot_name
        if ask:
            msg = "Would you like to use the plot-level properties of "
            msg += plot_name + ", or use the properties you have specified?"
            choices = []
            choices.append("Use properties of " + plot_name)
            choices.append("Use the properties I have specified")
            tao_message_box(
                self.root,
                self,
                ans_var,
                title="Plot parameters",
                message=msg,
                choices=choices,
            )
            if ans_var.get() == choices[1]:
                use_plot_props = None
        # Copy in plot properties if necessary
        self.handler_block = True
        if use_plot_props is not None:
            plot1 = tao_parameter_dict(
                self.pipe.cmd_in("python plot1 " + use_plot_props).splitlines()
            )
            for w in self.plot_param_list:
                if w.param.name in plot1.keys():
                    w.param_copy(plot1[w.param.name])
        # Unblock handlers and call them now
        self.handler_block = False
        self.plot_name_handler()
        self.x_axis_type_handler(skip_graph_handlers=True)
        # Delete old graphs if requested
        if c4:
            for j in range(len(self.graph_frame.tab_list)):
                self.graph_frame.remove_tab(0, destroy=True)
        # Copy the graphs
        for i in range(len(clone_graphs)):
            graph = clone_graphs[i]
            # add a new tab if necessary
            if c4:
                if i >= len(self.graph_frame.tab_list):
                    # print("ADDING GRAPH TAB")
                    self.graph_frame.add_tab(i, self.graph_frame)
            else:
                # print("ADDING GRAPH TAB")
                self.graph_frame.add_tab(i, self.graph_frame)
            # print("CLONING GRAPH")
            graph = self.clone_plot.get() + "." + graph
            self.graph_frame.tab_list[i].clone(graph)
        # Switch to first tab
        self.graph_frame.notebook.select(0)

    def create_template(self, event=None):
        """
        Reads the data input by the user and creates the plot template in tao
        """
        # Input validation (more TODO)
        messages = []
        if self.plot_name_handler():
            messages.append("Please check plot name")
        for graph_frame in self.graph_frame.tab_list:
            # Check names
            if graph_frame.name_handler():
                name_m = "Please check graph names."
                if name_m not in messages:
                    messages.append(name_m)
            # Check for semicolons in any fields
            semi_message = "Semicolons not allowed in any input field"
            caret_message = "Carets not allowed in any input field"
            curve_name_m = "Curve names cannot contain whitespace"
            broken = False  # Used to break out of the below for loops
            # Check for semicolons/carets
            for ttp in (
                graph_frame.head_wids
                + graph_frame.wids[graph_frame.type]
                + graph_frame.style_wids
            ):
                if str(ttp.tk_var.get()).find(";") != -1:
                    messages.append(semi_message)
                    broken = True
                    break
                if str(ttp.tk_var.get()).find("^") != -1:
                    messages.append(caret_message)
                    broken = True
                    break
            for curve_frame in graph_frame.curve_frame.tab_list:
                if broken:
                    break
                curve_list = (
                    curve_frame.head_wids
                    + curve_frame.wids[self.x_axis_type][graph_frame.type]
                    + curve_frame.style_wids
                )
                for ttp in curve_list:
                    if str(ttp.tk_var.get()).find(";") != -1:
                        messages.append(semi_message)
                        broken = True
                        break
                    if str(ttp.tk_var.get()).find("^") != -1:
                        messages.append(caret_message)
                        broken = True
                        break
                    if (str(ttp.tk_var.get()).find(" ") != -1) and (ttp.param.name == "name"):
                        messages.append(curve_name_m)
                        broken = True
                        break
                if broken:
                    break
        for m in messages:
            messagebox.showwarning("Error", m, parent=self)
        if messages != []:
            return
        # Get the appropriate template index
        if self.write_var.get() == "new":
            plot_list_t = self.pipe.cmd_in("python plot_list t").splitlines()
            plot_ix = plot_list_t[-1].split(";")[0]
            plot_ix = "@T" + str(int(plot_ix) + 1)
            # print("Writing new template")
            # print("Assigning index " + plot_ix)
        elif self.write_var.get() == "overwrite":
            plot_ix = self._overwrite_ix
        else:  # self.write_var == self
            plot_ix = self._plot_id
        self._created_plot_ix = plot_ix
        # Create the template
        n_graph = str(len(self.graph_frame.tab_list))
        cmd_str = "python plot_plot_manage " + plot_ix + "^^"
        cmd_str += self.name + "^^" + n_graph
        for graph_frame in self.graph_frame.tab_list:
            cmd_str += "^^" + graph_frame.name
        self.pipe.cmd_in(cmd_str)
        # Set the plot properties (but not name)
        set_list = []
        for ttp in self.plot_param_list:
            if ttp.param.name != "name":
                set_list.append(ttp)
        tao_set(set_list, "set plot " + plot_ix + " ", self.pipe, overide=True)
        # Set graph properties
        for gf in self.graph_frame.tab_list:
            graph_name = plot_ix + "." + gf.name
            # Set graph properties (but not name or n_curve)
            set_list = []
            for ttp in gf.head_wids + gf.wids[gf.type] + gf.style_wids:
                if ttp.param.name != "name":
                    set_list.append(ttp)
            tao_set(set_list, "set graph " + graph_name + " ", self.pipe, overide=True)
            # Create curves if appropriate
            if gf.type not in ["floor_plan", "lat_layout"]:
                curve_nums = range(1, len(gf.curve_frame.tab_list) + 1)
                for c in curve_nums:
                    curve = gf.curve_frame.tab_list[c - 1]
                    if curve.name == "":  # default to c1, c2, etc
                        curve_name = "c" + str(c)
                    else:
                        curve_name = curve.name
                    self.pipe.cmd_in(
                        "python plot_curve_manage "
                        + graph_name
                        + "^^"
                        + str(c)
                        + "^^"
                        + curve_name
                    )
                    curve_name = graph_name + "." + curve_name
                    # Set curve properties (but not the name)
                    set_list = []
                    for ttp in (
                        curve.head_wids
                        + curve.wids[self.x_axis_type][gf.type]
                        + curve.style_wids
                    ):
                        if ttp.param.name != "name":
                            set_list.append(ttp)
                    tao_set(
                        set_list,
                        "set curve " + curve_name + " ",
                        self.pipe,
                        overide=True,
                    )
        # Refresh plot-related windows
        for win in self.root.refresh_windows["plot"]:
            win.refresh()

    def create_and_plot(self, event=None):
        self.create_template()
        # Take the appropriate actions depending on the plotting mode
        if self.root.plot_mode == "matplotlib":
            if self.mode == "R":
                # Plot is already placed, just move it to top
                # Get region name
                plot_list_r = self.pipe.cmd_in("python plot_list r").splitlines()
                for i in range(len(plot_list_r)):
                    plot_list_r[i] = plot_list_r[i].split(";")
                ix = self._created_plot_ix[2:]  # without '@R'
                reg = plot_list_r[int(ix) - 1][1]
                for win in self.root.refresh_windows["plot"]:
                    if isinstance(win, tao_plot_window):
                        if win.region == reg:
                            win.lift()
                            break
            else:
                win = tao_plot_window(self.root, self._created_plot_ix, self.pipe)
        elif self.root.plot_mode == "pgplot/plplot":
            # Open a pgplot_place_window
            win = tao_pgplot_place_window(self.root, self.name, self.pipe)

    def plot_name_handler(self, event=None):
        """
        Reads the plot name into self.name, and warns the user if left blank
        """
        if self.handler_block:
            return
        name = self.plot_param_list[self.ixd["name"]].tk_var.get().strip()
        self.name_warning_1.grid_forget()
        self.name_warning_2.grid_forget()
        if name == "":
            self.name_warning_1.grid(
                row=self.ixd["name"] + self.plot_frame_offset, column=2, sticky="W"
            )
        elif name.find(" ") != -1:
            self.name_warning_2.grid(
                row=self.ixd["name"] + self.plot_frame_offset, column=2, sticky="W"
            )
        else:
            self.name = name

    def x_axis_type_handler(self, *args, **kwargs):
        """
        Sets self.x_axis_type to the selected x_axis_type
        Pass the keyword argument skip_graph_handlers=True to skip graph_type handlers
        """
        if self.handler_block:
            return
        self.x_axis_type = self.plot_param_list[self.ixd["x_axis_type"]].tk_var.get()
        if ("skip_graph_handlers" in kwargs.keys()) and kwargs["skip_graph_handlers"]:
            return
        # Run graph_type_handler for each child graph
        for graph in self.graph_frame.tab_list:
            graph.graph_type_handler()

    def _index_trace(self, *args):
        """
        Updates self._plot_id when self.plot_var changes
        (self.plot_var contains actual plot name, self._plot_id is e.g. @T3)
        """
        ix = self._index_list[self._plot_display_list.index(self.plot_var.get())]
        self._plot_id = "@" + self.mode + str(ix)

    def _overwrite_trace(self, *args):
        """
        Updates self._overwrite_ix when self.overwrite_var changes
        """
        ix = self.existing_plot_templates.index(self.overwrite_var.get()) + 1
        self._plot_id = "@T" + str(ix)

    def refresh(self, event=None):
        """
        In T/R mode, reloads plot properties from Tao
        In N mode, does nothing
        """
        if self.mode == "N":
            return
        else:
            if self.plot_var.get() in self._plot_display_list:
                # Make sure self._plot_id is updated
                self._index_trace()
                # Load plot by spoofing a clone
                self.clone_plot.set(self._plot_id)
                self.clone_plot_method(ask=False)
                self.clone_plot.set("None")


class new_graph_frame(tk.Frame):
    """
    New and improved frame for editing graph properties
    """

    def __init__(self, parent, plot):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.plot = plot
        self.pipe = plot.pipe
        self.handler_block = False
        self._uf = tk.Frame(self)  # Used to make graph frame and curve notebook uniform width
        self._uf.grid(row=0, column=0, sticky="NSEW")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)  # , uniform="uf")
        self.grid_columnconfigure(1, weight=1)  # , uniform="uf")
        self._scroll_frame = tao_scroll_frame(self._uf)
        self.name = "New_graph"
        # Default to first type compatible with self.plot.x_axis_type
        self.type = self.plot.compat_dict[self.plot.x_axis_type][0]

        # TEMPORARY
        def f(e):
            self.handler_block = False

        self.bind_all("<Control-b>", f)

        # Delete button
        tk.Button(self._uf, text="DELETE THIS GRAPH", fg="red", command=self.delete).grid(
            row=0, column=0, columnspan=3, sticky="EW"
        )

        # Duplicate button
        tk.Button(self._uf, text="Duplicate this graph", command=self.duplicate).grid(
            row=1, column=0, columnspan=3, sticky="EW"
        )

        self._uf.grid_columnconfigure(2, weight=1)

        # Setup
        self.graph_frame = self._scroll_frame.frame
        self.graph_frame.grid_columnconfigure(1, weight=1)

        # Helper functions
        def graph_ttp(x):
            """Shortcut for commonly used construct"""
            p = str_to_tao_param(x)
            if x in self.head_wids:
                return tk_tao_parameter(p, self._uf, self.pipe)
            else:
                return tk_tao_parameter(p, self.graph_frame, self.pipe)

        def qp_axis_props(x):
            """Adds the props of a qp-axis-struct to the parameter string x"""
            if self.plot.root.plot_mode == "matplotlib":
                x += ";label;STR;;min;REAL;;max;REAL;;draw_label;LOGIC;T;draw_numbers;LOGIC;T"
            else:
                x += ";label;STR;;min;REAL;;max;REAL;;number_offset;REAL;"
                x += ";label_offset;REAL;;label_color;ENUM;;major_tick_len;REAL;"
                x += ";minor_tick_len;REAL;;major_div;INT;;major_div_nominal;INT;"
                x += ";minor_div;INT;;minor_div_max;INT;;places;INT;;axis^type;ENUM;"
                x += ";bounds;ENUM;;tick_side;INUM;;number_side;INUM;"
                x += ";draw_label;LOGIC;T;draw_numbers;LOGIC;T"
            return x

        def floor_plan_props(x):
            """Adds the properties of a floor_plan struct to x"""
            x += ";view;ENUM;zx;rotation;REAL;0;flip_label_side;LOGIC;F"
            x += ";size_is_absolute;LOGIC;F;draw_building_wall;LOGIC;T"
            x += ";draw_only_first_pass;LOGIC;F;correct_distortion;LOGIC;T"
            x += ";orbit_scale;REAL;0;orbit_color;ENUM;red;orbit_width;INT;1;orbit_pattern;ENUM;solid"
            return x

        def graph_label_maker(x):
            """Helper function"""
            if x in self.head_labels:
                return tk.Label(self._uf, text=x)
            else:
                return tk.Label(self.graph_frame, text=x)

        # Graph widgets

        # Basics
        self.head_wids = ["name;STR;T;", "graph^type;ENUM;T;", "title;STR;T;"]
        self.head_labels = ["Graph name:", "Graph type:", "Graph title"]
        self.head_wids = list(map(graph_ttp, self.head_wids))
        self.head_wids[1].tk_var.set(self.type)
        self.head_labels = list(map(graph_label_maker, self.head_labels))
        # Type-specific options
        self.wids = {}
        self.labels = {}
        # Data graphs
        self.wids["data"] = [
            "component;COMPONENT;T;model",
            "ix_universe;INT;T;",
            "draw_only_good_user_data_or_vars;LOGIC;T;T",
        ]
        self.labels["data"] = [
            "Component:",
            "Universe:",
            "Draw only good_user data/variables:",
        ]
        self.wids["data"] = list(map(graph_ttp, self.wids["data"]))
        self.labels["data"] = list(map(graph_label_maker, self.labels["data"]))
        # Floor plans
        self.wids["floor_plan"] = [
            qp_axis_props("x2;STRUCT;T"),
            "ix_universe;INT;T;",
            floor_plan_props("floor_plan;STRUCT;T"),
        ]
        # "floor_plan_rotation;REAL;T;",
        # "floor_plan_view;STR;T;zx",
        # "floor_plan_orbit_scale;REAL;T;",
        # "floor_plan_orbit_color;STR;T;",
        # "floor_plan_flip_label_side;LOGIC;T;F",
        # "floor_plan_size_is_absolute;LOGIC;T;F",
        # "floor_plan_draw_only_first_pass;LOGIC;T;F"]
        self.labels["floor_plan"] = ["X2-axis:", "Universe:", "Floor plan settings:"]
        # "Rotation:", "View:", "Orbit scale:", "Orbit color:",
        # "Flip label side:", "Absolute size:", "Draw only first pass:"]
        self.wids["floor_plan"] = list(map(graph_ttp, self.wids["floor_plan"]))
        self.labels["floor_plan"] = list(map(graph_label_maker, self.labels["floor_plan"]))
        # Lat layouts
        self.wids["lat_layout"] = ["ix_universe;INT;T;", "ix_branch;INT;T;"]
        self.labels["lat_layout"] = ["Universe:", "Branch:"]
        self.wids["lat_layout"] = list(map(graph_ttp, self.wids["lat_layout"]))
        self.labels["lat_layout"] = list(map(graph_label_maker, self.labels["lat_layout"]))
        # Dynamic aperture
        self.wids["dynamic_aperture"] = ["ix_universe;INT;T;"]
        self.labels["dynamic_aperture"] = ["Universe:"]
        self.wids["dynamic_aperture"] = list(map(graph_ttp, self.wids["dynamic_aperture"]))
        self.labels["dynamic_aperture"] = list(
            map(graph_label_maker, self.labels["dynamic_aperture"])
        )
        # Histograms
        self.wids["histogram"] = ["ix_universe;INT;T;"]
        self.labels["histogram"] = ["Universe:"]
        self.wids["histogram"] = list(map(graph_ttp, self.wids["histogram"]))
        self.labels["histogram"] = list(map(graph_label_maker, self.labels["histogram"]))
        # Phase space plots
        self.wids["phase_space"] = ["ix_universe;INT;T;"]
        self.labels["phase_space"] = ["Universe:"]
        self.wids["phase_space"] = list(map(graph_ttp, self.wids["phase_space"]))
        self.labels["phase_space"] = list(map(graph_label_maker, self.labels["phase_space"]))
        # Graph styling
        self.style_wids = [
            qp_axis_props("x;STRUCT;T"),
            qp_axis_props("y;STRUCT;T"),
            qp_axis_props("y2;STRUCT;T"),
            "clip;LOGIC;T;T",
            "draw_axes;LOGIC;T;T",
            "draw_grid;LOGIC;T;T",
            "allow_wrap_around;LOGIC;T;F",
            "symbol_size_scale;REAL;T;",
            "floor_plan%correct_distortion;LOGIC;T;F",
            "x_axis_scale_factor;REAL;T;",
        ]
        self.style_labels = [
            "X-axis:",
            "Y-axis:",
            "Y2-axis",
            "Clip at boundary:",
            "Draw axes:",
            "Draw grid:",
            "Allow wrap-around:",
            "Symbol size scale:",
            "Correct xy distortion:",
            "X-axis scale factor:",
        ]
        if self.plot.root.plot_mode != "matplotlib":
            self.style_wids = [
                "box;STR;T;",
                "margin;REAL;T;",
                "scale_margin;REAL;T;",
            ] + self.style_wids
            self.style_labels = ["Box:", "Margin:", "Scale Margin:"] + self.style_labels
        self.style_wids = list(map(graph_ttp, self.style_wids))
        self.style_labels = list(map(graph_label_maker, self.style_labels))

        # Grid head widgets
        for i in range(len(self.head_wids)):
            self.head_labels[i].grid(row=i + 2, column=0, sticky="W")
            self.head_wids[i].tk_wid.grid(row=i + 2, column=1, sticky="EW")

        # Warning labels
        # (defined here to be gridded/ungridded as necessary)
        self.name_warning_1 = tk.Label(self._uf, text="Must not be empty")
        self.name_warning_2 = tk.Label(self._uf, text="Graph name already in use")
        self.name_warning_3 = tk.Label(self._uf, text="Cannot contain whitespace")

        # Responses to edits
        self.head_wids[0].tk_wid.bind("<FocusOut>", self.name_handler)
        self.head_wids[1].tk_var.trace("w", self.graph_type_handler)

        # Curves
        self.curve_frame = tabbed_frame(self, lambda arg: new_curve_frame(arg, self))

        # Element shapes (for lat_layouts and floor_plans)
        self.lat_layout_frame = ele_shape_frame(self, self.plot.root, self.pipe, "lat_layout")
        self.floor_plan_frame = ele_shape_frame(self, self.plot.root, self.pipe, "floor_plan")

        # Grid everything else
        self._scroll_frame.grid(
            row=2 + len(self.head_wids), column=0, columnspan=3, sticky="NSEW"
        )
        self._uf.grid_rowconfigure(2 + len(self.head_wids), weight=1)
        self.refresh()
        self.update_idletasks()
        self.refresh()  # called again to get the head widgets sized correctly

    def refresh(self):
        """
        Grids the appropriate widgets for the current graph type,
        grids self.curve_frame or self.ele_frame as appropriate,
        then calls refresh for each of the curves if appropriate
        (i.e. if self.type not in ['lat_layout', 'floor_plan'])
        """
        # Ungrid the non-style widgets
        for child in self.graph_frame.winfo_children():
            child.grid_forget()
        # Grid the appropriate widgets
        for i in range(len(self.wids[self.type])):
            self.labels[self.type][i].grid(row=i, column=0, sticky="W")
            self.wids[self.type][i].tk_wid.grid(row=i, column=1, sticky="EW")
        offset = i + 1
        # Grid the style widgets
        for i in range(len(self.style_wids)):
            ix = i + offset
            self.style_labels[i].grid(row=ix, column=0, sticky="W")
            self.style_wids[i].tk_wid.grid(row=ix, column=1, sticky="EW")
        # self.update_idletasks() #let widgets obtain their sizes
        # Set label widths properly for head widgets
        label_width = 0
        for child in self.graph_frame.grid_slaves():
            if isinstance(child, tk.Label):
                label_width = max(label_width, child.winfo_width())
        self._uf.grid_columnconfigure(0, minsize=label_width)
        # Swap between self.curve_frame or self.ele_frame as necessary
        self.curve_frame.grid_forget()
        self.lat_layout_frame.grid_forget()
        self.floor_plan_frame.grid_forget()
        # print("At new_graph_frame.refresh(): self.type = " + self.type)
        if self.type == "lat_layout":
            self.lat_layout_frame.grid(row=0, column=1, sticky="NSEW")
        elif self.type == "floor_plan":
            self.floor_plan_frame.grid(row=0, column=1, sticky="NSEW")
        else:
            self.curve_frame.grid(row=0, column=1, sticky="NSEW")
            for curve in self.curve_frame.tab_list:
                curve.refresh()

    def delete(self, ask=True, event=None):
        """
        Deletes this graph frame
        Call with ask = False to skip confirmation
        """
        # Ask for confirmation
        if ask:
            ans = messagebox.askokcancel(
                "Delete " + self.name,
                "Delete this graph and its associated curves?",
                parent=self.parent,
            )
            if not ans:
                return

        # Remove from tabbed frame
        self.parent.remove_tab(self.parent.tab_list.index(self))

        # Destroy self
        self.destroy()

    def duplicate(self, event=None):
        """
        Adds a new graph_frame to self.parent.graph_frame that is a copy of
        this frame, and changes focus to that frame
        """
        # Don't run any handlers for this graph_frame
        # self.handler_block = True
        self.plot.graph_frame.add_tab(
            len(self.plot.graph_frame.tab_list), self.plot.graph_frame
        )
        new_frame = self.plot.graph_frame.tab_list[-1]
        # Copy graph widgets
        # Head widgets:
        for i in range(len(self.head_wids)):
            w = self.head_wids[i]
            if w.param.name == "name":
                new_frame.head_wids[i].tk_var.set(w.tk_var.get() + "_copy")
            else:
                new_frame.head_wids[i].copy(w)
        # Content widgets:
        for key in self.wids.keys():
            for i in range(len(self.wids[key])):
                w = self.wids[key][i]
                new_frame.wids[key][i].copy(w)
        # Style widgets:
        for i in range(len(self.style_wids)):
            w = self.style_wids[i]
            new_frame.style_wids[i].copy(w)
        # Run all input validation handlers
        self.parent.notebook.select(self.plot.graph_frame.tab_list.index(new_frame))
        self.update_idletasks()
        new_frame.name_handler()
        new_frame.graph_type_handler()
        # Copy curve widgets
        for curve in self.curve_frame.tab_list:
            curve.duplicate(target=new_frame)

    def clone(self, graph, event=None):
        """
        Clone an existing graph (already defined in tao, use self.duplicate() to
        make copies of graphs already defined in the new plot template window
        Does not clone plot properties
        """
        # Turn off event handlers
        self.handler_block = True
        # Grab the graph info
        plot_graph = self.pipe.cmd_in("python plot_graph " + graph)
        raw_graph_dict = tao_parameter_dict(plot_graph.splitlines())
        # Remove prefixes for enums and inums
        graph_dict = {}
        for key in raw_graph_dict.keys():
            gkey = key.split("^")[-1]
            graph_dict[gkey] = raw_graph_dict[key]
        # First set the head widgets
        for w in self.head_wids:
            if w.param.name in graph_dict.keys():
                w.param_copy(graph_dict[w.param.name])
        # Update self.name and self.type
        self.name = self.head_wids[0].tk_var.get()
        self.type = self.head_wids[1].tk_var.get()
        # Copy the type-specific graph info
        for w in self.wids[self.type]:
            if w.param.name in graph_dict.keys():
                w.param_copy(graph_dict[w.param.name])
        # Copy the style related graph info
        for w in self.style_wids:
            if w.param.name in graph_dict.keys():
                w.param_copy(graph_dict[w.param.name])
        # Unblock handlers, run and refresh
        self.handler_block = False
        self.graph_type_handler()
        self.refresh()
        # Copy the curves if necessary
        if ("num_curves" in graph_dict.keys()) and (graph_dict["num_curves"] is not None):
            # Remove existing curves
            for i in range(len(self.curve_frame.tab_list)):
                self.curve_frame.remove_tab(0, destroy=True)
            num_curves = graph_dict["num_curves"].value
            for i in range(num_curves):
                # Add a new curve if necessary:
                if i >= len(self.curve_frame.tab_list):
                    self.curve_frame.add_tab(i, self.curve_frame)
                # Clone the curve
                curve = (
                    self.plot.name
                    + "."
                    + self.name
                    + "."
                    + graph_dict["curve[" + str(i + 1) + "]"].value
                )
                self.curve_frame.tab_list[i].clone(curve)
            # Switch to first curve
            self.curve_frame.notebook.select(0)
        # Run name handler now in case the name is already taken
        # (don't want to lose self.name for curve cloning)
        self.name_handler()

    def graph_type_handler(self, *args):
        """
        Checks that plot.x_axis_type is compatible with the selected graph type.
        If it is, updates self.type and calls self.refresh()
        If it is not, warns the user of the incompatibility.
        """
        if self.handler_block:
            return
        self.handler_block = True
        new_type = self.head_wids[1].tk_var.get()
        cdict = self.plot.compat_dict
        if new_type in cdict[self.plot.x_axis_type]:
            self.type = new_type
            self.refresh()
        else:
            title = "X-axis/graph type mismatch"
            msg = "The X-axis type you have selected (" + self.plot.x_axis_type
            msg += ") is not compatible with the graph type you have selected for "
            msg += self.name + " (" + new_type + ").\n"
            msg += "The " + self.plot.x_axis_type + " X-axis type is compatible with "
            msg += "the following graph types:"
            for t in cdict[self.plot.x_axis_type]:
                msg += "\n" + t
            messagebox.showwarning(title, msg, parent=self.plot)
        self.handler_block = False

    def name_handler(self, event=None):
        """
        Checks that a good name has been input for the graph and
        updates self.name as necessary.  Warns the user if the name
        is taken or empty
        """
        if self.handler_block:
            return
        new_name = self.head_wids[0].tk_var.get().strip()
        self.name_warning_1.grid_forget()
        self.name_warning_2.grid_forget()
        self.name_warning_3.grid_forget()
        # Check what names are taken for this plot
        taken_names = []
        for graph in self.parent.tab_list:
            taken_names.append(graph.name)
        if new_name == "":
            self.name_warning_1.grid(row=2, column=2, sticky="W")
            self.name = "New_graph"
        elif new_name.find(" ") != -1:
            self.name_warning_3.grid(row=2, column=2, sticky="W")
        elif (taken_names.count(new_name) > 1) or (
            (taken_names.count(new_name) == 1) and (new_name != self.name)
        ):
            self.name_warning_2.grid(row=2, column=2, sticky="W")
        else:
            self.name = new_name
        # Update the tab text for this graph
        self.parent.update_name(self.parent.tab_list.index(self))


class new_curve_frame(tk.Frame):
    """
    Provides a frame to configure curve properties as necessary
    """

    def __init__(self, parent, graph):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.graph = graph
        self.pipe = graph.pipe
        self.handler_block = False
        self._scroll_frame = tao_scroll_frame(self)
        self.name = "New_curve"
        self.grid_columnconfigure(1, weight=1)

        # Delete button
        self.delete_b = tk.Button(
            self, text="DELETE THIS CURVE", fg="red", command=self.delete
        )

        # Duplicate button
        self.dup_b = tk.Button(self, text="Duplicate this curve", command=self.duplicate)

        self.delete_b.grid(row=0, column=0, columnspan=3, sticky="EW")
        self.dup_b.grid(row=1, column=0, columnspan=3, sticky="EW")
        self.grid_columnconfigure(2, weight=1)

        # Curve configuration widgets
        self.curve_frame = self._scroll_frame.frame
        self.curve_frame.grid_columnconfigure(1, weight=1)

        # Helper functions
        def curve_ttp(x):
            """Returns a tk_tao_parameter for the string x"""
            p = str_to_tao_param(x)
            if x in self.head_wids:
                return tk_tao_parameter(p, self, self.pipe)
            else:
                return tk_tao_parameter(p, self.curve_frame, self.pipe)

        def curve_label(x):
            """Returns a tk.Label for the string x"""
            if x in self.head_labels:
                return tk.Label(self, text=x)
            else:
                return tk.Label(self.curve_frame, text=x)

        # Widget definitions
        # General
        self.head_wids = ["name;STR;T;"]
        self.head_labels = ["Name:"]
        self.head_wids = list(map(curve_ttp, self.head_wids))
        self.head_labels = list(map(curve_label, self.head_labels))
        # X-axis/graph type specific settings
        # Dictionary of dictionary of lists (self.wids[key1][key2][ix])
        # key1: x_axis_type; key2: graph_type
        self.wids = {}
        self.labels = {}
        for key in [
            "index",
            "ele_index",
            "lat",
            "var",
            "s",
            "floor",
            "phase_space",
            "histogram",
            "data",
            "none",
        ]:
            self.wids[key] = {}
            self.labels[key] = {}
        # Normal data plot
        self.wids["index"]["data"] = [
            "data_source;ENUM;T;",
            "data_type_x;DAT_TYPE_Z;T;",
            "data_type;DAT_TYPE;T;",
            "component;COMPONENT;T;model",
        ]
        self.labels["index"]["data"] = [
            "Data source:",
            "X data type:",
            "Y data type:",
            "Component:",
            "Data index:",
        ]
        # Data slice
        self.wids["data"]["data"] = [
            "data_source;ENUM;F;data",
            "data_type_x;DAT_TYPE_E;T;",
            "data_type;DAT_TYPE_E;T;",
            "data_index;DAT_TYPE_E;T;",
            "component;COMPONENT;T;model",
            "ele_ref_name;STR;T;",
        ]
        self.labels["data"]["data"] = [
            "Data source:",
            "X data type:",
            "Y data type:",
            "Data index:",
            "Component:",
            "Reference Element:",
        ]
        # Data vs lat/var
        self.wids["lat"]["data"] = [
            "data_source;ENUM;F;data",
            "data_type_x;STR;T;",
            "data_type;STR;T;",
            "component;COMPONENT;T;model",
            "ele_ref_name;STR;T;",
        ]
        self.labels["lat"]["data"] = [
            "Data source:",
            "X data type:",
            "Y data type:",
            "Data index:",
            "Component:",
            "Reference Element:",
        ]
        # Histograms
        self.wids["histogram"]["histogram"] = [
            "data_source;ENUM;T;",
            "data_type;ENUM_Z;T;",
            "ele_ref_name;STR;T;",
            "hist;STRUCT;T;density_normalized;LOGIC;T;weight_by_charge;LOGIC;T;number;INT;100;width;INT;",
        ]
        self.labels["histogram"]["histogram"] = [
            "Data source:",
            "Data type:",
            "Reference element:",
            "Bin settings:",
        ]
        # Phase space plots
        self.wids["phase_space"]["phase_space"] = [
            "data_source;ENUM;T;",
            "data_type_x;ENUM_Z;T;",
            "data_type;ENUM_Z;T;",
            "ele_ref_name;STR;T;",
            "use_z_color;LOGIC;T;F",
            "data_type_z;ENUM_Z;T;",
            "z_color0;REAL;T;0",
            "z_color1;REAL;T;0",
            "autoscale_z_color;LOGIC;T;T",
        ]
        self.labels["phase_space"]["phase_space"] = [
            "Data source:",
            "X data type:",
            "Y data type:",
            "Reference element:",
            "Use z color:",
            "Color data type:",
            "Color min:",
            "Color max:",
            "Autoscale color:",
        ]
        # Map strings in self.wids and self.labels to tk widgets
        for key1 in self.wids.keys():
            for key2 in self.wids[key1].keys():
                self.wids[key1][key2] = list(map(curve_ttp, self.wids[key1][key2]))
                self.labels[key1][key2] = list(map(curve_label, self.labels[key1][key2]))
        # Copy lists as necessary
        self.wids["ele_index"]["data"] = self.wids["s"]["data"] = self.wids["index"]["data"]
        self.labels["ele_index"]["data"] = self.labels["s"]["data"] = self.labels["index"][
            "data"
        ]
        self.wids["var"]["data"] = self.wids["lat"]["data"]
        self.labels["var"]["data"] = self.labels["lat"]["data"]
        self.wids["phase_space"]["histogram"] = self.wids["histogram"]["histogram"]
        self.labels["phase_space"]["histogram"] = self.labels["histogram"]["histogram"]
        # Set up empty lists for other axis/graph type compbos to prevent key errors
        x_types = [
            "index",
            "ele_index",
            "s",
            "data",
            "lat",
            "var",
            "floor",
            "phase_space",
            "histogram",
            "none",
        ]
        g_types = [
            "data",
            "lat_layout",
            "floor_plan",
            "dynamic_aperture",
            "histogram",
            "phase_space",
        ]
        for x in x_types:
            if x not in self.wids.keys():
                self.wids[x] = {}
                self.labels[x] = {}
            for g in g_types:
                if g not in self.wids[x].keys():
                    self.wids[x][g] = []
                    self.labels[x][g] = []

        # Trace data_source widgets to data_source_handler and keep a list of them
        self.data_sources = {}
        for pkey in self.wids.keys():
            self.data_sources[pkey] = {}
            for gkey in self.wids[pkey].keys():
                for w in self.wids[pkey][gkey]:
                    if w.param.name == "data_source":
                        # Trace
                        w.tk_var.trace("w", self.data_source_handler)
                        # Add to list
                        self.data_sources[pkey][gkey] = w

        # Style
        self.style_wids = [
            "units;STR;T;",
            "legend_text;STR;T;",
            "y_axis_scale_factor;REAL;T;",
            "use_y2;LOGIC;T;F",
            "draw_line;LOGIC;T;T",
            "draw_symbols;LOGIC;T;T;",
            "draw_symbol_index;LOGIC;T;F",
            "line;STRUCT;T;width;INT;1;color;ENUM;;line^pattern;ENUM;",
            "symbol;STRUCT;T;symbol^type;ENUM;;height;REAL;6.0;color;ENUM;;fill_pattern;ENUM;;line_width;INT;1",
            "symbol_every;INT;T;",
            "smooth_line_calc;LOGIC;T;",
        ]
        self.style_labels = [
            "Units:",
            "Legend text:",
            "Y axis scale factor:",
            "Use Y2 axis:",
            "Draw line:",
            "Draw symbols:",
            "Draw symbol index:",
            "Line:",
            "Symbols:",
            "Symbol frequency:",
            "Smooth line calc:",
        ]
        self.style_wids = list(map(curve_ttp, self.style_wids))
        self.style_labels = list(map(curve_label, self.style_labels))

        # Grid head widgets
        for i in range(len(self.head_wids)):
            self.head_labels[i].grid(row=i + 2, column=0, sticky="W")
            self.head_wids[i].tk_wid.grid(row=i + 2, column=1, sticky="EW")

        # Warning labels
        self.name_warning_1 = tk.Label(self, text="Must not be empty")
        self.name_warning_2 = tk.Label(self, text="Curve name already in use")
        self.name_warning_3 = tk.Label(self, text="Cannot contain whitespace")

        # Responses to edits
        self.head_wids[0].tk_wid.bind("<FocusOut>", self.name_handler)

        # Grid everything else
        self._scroll_frame.grid(
            row=2 + len(self.head_wids), column=0, columnspan=3, sticky="NSEW"
        )
        self.grid_rowconfigure(2 + len(self.head_wids), weight=1)
        self.refresh()
        self.update_idletasks()
        self.refresh()  # called again to set label widths properly

    def refresh(self):
        """
        Draws appropriate widgets to the frame depending on graph.type and
        plot.x_axis_type.  The parent graph is expected to verify that
        the graph and x_axis type are compatible before calling this method
        """
        # Remove existing widgets
        for child in self.curve_frame.winfo_children():
            child.grid_forget()

        # Grid the x-axis/graph type specific widgets
        graph_type = self.graph.type
        x_axis_type = self.graph.plot.x_axis_type
        i = 0  # In case self.wids[x_axis_type][graph_type] is empty
        # print("At new_curve_frame.refresh(): x_axis_type = " + x_axis_type)
        # print("At new_curve_frame.refresh(): graph_type = " + graph_type)
        # print(self.wids)
        # print(self.wids.keys())
        # print(self.wids['s'].keys())
        for i in range(len(self.wids[x_axis_type][graph_type])):
            self.labels[x_axis_type][graph_type][i].grid(row=i, column=0, sticky="W")
            self.wids[x_axis_type][graph_type][i].tk_wid.grid(row=i, column=1, sticky="EW")
        offset = i + 1

        # Grid the style widgets
        for i in range(len(self.style_wids)):
            ix = i + offset
            self.style_labels[i].grid(row=ix, column=0, sticky="W")
            self.style_wids[i].tk_wid.grid(row=ix, column=1, sticky="EW")

        # Set head label widths properly
        label_width = 0
        for child in self.curve_frame.grid_slaves():
            if child.grid_info()["column"] == 0:
                label_width = max(label_width, child.winfo_width())
        self.grid_columnconfigure(0, minsize=label_width)

    def clone(self, curve):
        """
        Clone the specified curve
        """
        # Turn off event handlers
        self.handler_block = True
        # Grab the curve info
        plot_curve = self.pipe.cmd_in("python plot_curve " + curve)
        raw_curve_dict = tao_parameter_dict(plot_curve.splitlines())
        # Remove prefixes for enums and inums
        curve_dict = {}
        for key in raw_curve_dict.keys():
            ckey = key.split("^")[-1]
            curve_dict[ckey] = raw_curve_dict[key]
        # First set the head widgets
        for w in self.head_wids:
            if w.param.name in curve_dict.keys():
                w.param_copy(curve_dict[w.param.name])
        # Copy the type-specific curve info
        graph_type = self.graph.type
        x_axis_type = self.graph.plot.x_axis_type
        for w in self.wids[x_axis_type][graph_type]:
            if w.param.name in curve_dict.keys():
                w.param_copy(curve_dict[w.param.name])
        # Copy the style related curve info
        for w in self.style_wids:
            if w.param.name in curve_dict.keys():
                w.param_copy(curve_dict[w.param.name])
        # Unblock handlers, run and refresh
        self.handler_block = False
        self.name_handler()
        self.refresh()

    def delete(self, ask=True):
        """
        Deletes this graph frame
        Call with ask = False to skip confirmation
        """
        # Ask for confirmation
        if ask:
            ans = messagebox.askokcancel(
                "Delete " + self.name, "Delete this curve?", parent=self.graph.plot
            )
            if not ans:
                return

        # Remove from tabbed frame
        self.parent.remove_tab(self.parent.tab_list.index(self))

        # Destroy self
        self.destroy()

    def duplicate(self, target=None):
        """
        Duplicates this curve into the graph_frame specified by target
        target defaults to this curve_frame's parent graph
        """
        if target is None:
            target = self.graph
        # Don't run any handlers for this curve_frame
        # self.handler_block = True
        target.curve_frame.add_tab(len(target.curve_frame.tab_list), target.curve_frame)
        new_frame = target.curve_frame.tab_list[-1]
        # Copy curve widgets
        # Head widgets:
        for i in range(len(self.head_wids)):
            w = self.head_wids[i]
            if w.param.name == "name":
                new_frame.head_wids[i].tk_var.set(w.tk_var.get() + "_copy")
            else:
                new_frame.head_wids[i].copy(w)
        # Content widgets:
        for pkey in self.wids.keys():
            for gkey in self.wids[pkey].keys():
                for i in range(len(self.wids[pkey][gkey])):
                    w = self.wids[pkey][gkey][i]
                    new_frame.wids[pkey][gkey][i].copy(w)
        # Style widgets:
        for i in range(len(self.style_wids)):
            w = self.style_wids[i]
            new_frame.style_wids[i].copy(w)
        # Run all input validation handlers
        self.parent.notebook.select(target.curve_frame.tab_list.index(new_frame))
        self.update_idletasks()
        new_frame.name_handler()

    def name_handler(self, event=None):
        """
        Checks that a good name has been input for the curve and
        updates self.name as necessary.  Warns the user if the name
        is taken or empty
        """
        if self.handler_block:
            return
        new_name = self.head_wids[0].tk_var.get().strip()
        self.name_warning_1.grid_forget()
        self.name_warning_2.grid_forget()
        self.name_warning_3.grid_forget()
        # Check what names are taken for this plot
        taken_names = []
        for curve in self.parent.tab_list:
            taken_names.append(curve.name)
        if new_name == "":
            self.name_warning_1.grid(row=2, column=2, sticky="W")
            self.name = "New_curve"
        elif new_name.find(" ") != -1:
            self.name_warning_3.grid(row=2, column=2, sticky="W")
        elif (taken_names.count(new_name) > 1) or (
            (taken_names.count(new_name) == 1) and (new_name != self.name)
        ):
            self.name_warning_2.grid(row=2, column=2, sticky="W")
        else:
            self.name = new_name
        # Update the tab text for this graph
        self.parent.update_name(self.parent.tab_list.index(self))

    def data_source_handler(self, *args):
        """
        Keeps DAT_TYPE widgets in line with their respective
        data_source widgets
        """
        for pkey in self.wids.keys():
            for gkey in self.wids[pkey].keys():
                for w in self.wids[pkey][gkey]:
                    if w.param.type in ["DAT_TYPE", "DAT_TYPE_E"]:
                        w._data_source = self.data_sources[pkey][gkey].tk_var.get()
                        w._s_refresh()


# ------------------------------------------------------------------------------------
class tao_pgplot_canvas(tk.Frame):
    """
    Provides a widget that represents the pgplot window
    This widget has three modes of operation:
    "config", "place", and "view"
    In "config" mode, the window is shown in its maximally
    divided state given the current number of rows and columns.
    I.e., if r12 and r1234 have plots in them, four rows and
    two columns will be shown, since r1234 is a four row, 2 column
    region, and r12 just happens to take up the space of the top four
    regions in this configuration. This mode does not display
    which plot is placed in which region.
    In "view" mode, the canvas is shown as it actually is.
    In the above example, r12 would be displayed as one contiguous region,
    and r1234, r1244, r2234, r2244 would be displayed below it.
    The regions also show which plots are currently placed in them.
    In "place" mode, the canvas is displayed in much the same way as in
    "view" mode, except that clicking on regions selects/deselcts them
    for plot placing.  Necessarily, functionality is also provided to
    subdivide combined regions into their smaller parts
    """

    def __init__(self, parent, mode, root, pipe, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.root = root
        self.pipe = pipe
        self.mode = mode

        self.width = 300
        self.height = 600

        self.page = tk.Canvas(self, width=self.width + 10, height=self.height + 10)
        # +10 for 5px of padding on each side
        self.page.pack(fill="both", expand=1)

        self.place_region = ""
        self.place_plot = ""

        self.refresh()

    def refresh(self, *args):
        """Redraws the pgplot page with the correct regions"""
        # Clear page
        for child in self.page.find_all():
            self.page.delete(child)

        # Get the regions to draw
        regions = self.pipe.cmd_in("python plot_list r").splitlines()
        for i in range(len(regions)):
            regions[i] = regions[i].split(";")
        # Create rectangles for non-empty regions:
        for r in regions:
            if r[3] == "T":
                xlo = 5 + float(r[4]) * self.width
                xhi = 5 + float(r[5]) * self.width
                # y values are measured from the bottom up
                ylo = 5 + (1 - float(r[7])) * self.height
                yhi = 5 + (1 - float(r[6])) * self.height
                self.page.create_rectangle(
                    xlo, ylo, xhi, yhi, fill="white", tags=tuple(r[1:3])
                )
                self.page.create_text(
                    (xlo + xhi) / 2,
                    (ylo + yhi) / 2,
                    text=r[1] + "\n" + r[2],
                    tags=tuple(["text"] + r[1:3]),
                )
        # Create a rectangle for self.place_region, and check which regions it overlaps
        overlapping = []
        for r in regions:
            if r[1] == self.place_region:
                xlo = 5 + float(r[4]) * self.width
                xhi = 5 + float(r[5]) * self.width
                # y values are measured from the bottom up
                ylo = 5 + (1 - float(r[7])) * self.height
                yhi = 5 + (1 - float(r[6])) * self.height
                for item in self.page.find_overlapping(xlo + 1, ylo + 1, xhi - 1, yhi - 1):
                    # print("Overlapping item tags:")
                    tags = self.page.gettags(item)
                    # print(tags)
                    if "text" not in tags:
                        self.page.itemconfig(item, fill="#e8645a")
                        overlapping.append(tags)

                # print("-------------------------")
                self.page.create_rectangle(xlo, ylo, xhi, yhi, fill="yellow")
                self.page.create_text(
                    (xlo + xhi) / 2,
                    (ylo + yhi) / 2,
                    text=self.place_region + "\n" + self.place_plot,
                )
                break
        return overlapping

        # -------------------------------

        # Get the correct regions to draw
        regions = []
        if self.mode in ["view", "place"]:
            # First place maximal number of regions
            # in case some are empty
            oldmode = self.mode
            self.mode = "config"
            self.refresh()
            # Now place the regions that are occupied
            self.mode = oldmode
            for r in self.root.placed.keys():
                if r.find("@R") != 0:
                    regions.append(r)
        elif self.mode == "config":
            # Take values from self.root.placed if
            # self.rownum etc are negative (unset),
            # otherwise use these values
            if self.rownum < 0:
                rnum = int(self.root.placed.pgplot_settings["rows"])
            else:
                rnum = self.rownum
            if self.colnum < 0:
                cnum = int(self.root.placed.pgplot_settings["columns"])
            else:
                cnum = self.colnum
            if self.latnum < 0:
                lnum = int(self.root.placed.pgplot_settings["lat_layouts"])
            else:
                lnum = self.latnum
            if (rnum == 2) and (cnum == 1) and (lnum == 0):
                # Special case for top and bottom
                regions = ["top", "bottom"]
            elif cnum == 1:
                for i in range(1, rnum + 1):
                    # rAB
                    regions.append("r" + str(i) + str(rnum))
            else:
                for i in range(1, rnum + 1):
                    for j in range(1, cnum + 1):
                        # rABCD
                        regions.append("r" + str(j) + str(cnum) + str(i) + str(rnum))
            # Add layout slots
            if lnum == 1:
                regions.append("layout")
            elif lnum == 2:
                regions.append("layout1")
                regions.append("layout2")

        # Testing
        # print(regions)
        for region in regions:
            if self.mode == "config":
                self.add_region(region, False)
            else:
                self.add_region(region, True)
        # Special case: the 3 row regions will cancel out some of the 4 row regions
        if "r13" in regions:
            for reg in ["r14", "r24", "r1214", "r2214", "r1224", "r2224"]:
                if reg in self.shown_regions.keys():
                    self.shown_regions[reg].grid_forget()
                    self.shown_regions.pop(reg)
        if "r23" in regions:
            for reg in ["r34", "r24", "r1234", "r2234", "r1224", "r2224"]:
                if reg in self.shown_regions.keys():
                    self.shown_regions[reg].grid_forget()
                    self.shown_regions.pop(reg)
        if "r33" in regions:
            for reg in ["r34", "r44", "r1234", "r2234", "r1244", "r2244"]:
                if reg in self.shown_regions.keys():
                    self.shown_regions[reg].grid_forget()
                    self.shown_regions.pop(reg)

    def add_region(self, region, include_plot):
        """
        Adds the region specified by name to the pgplot page.
        The name of the plot currently in the region will also
        be displayed if include_plot is True
        """
        b = 0
        if include_plot:
            if region in self.root.placed.keys():
                plotname = "\n" + self.root.placed[region]
            else:
                plotname = ""
        else:
            plotname = ""
        if region == "top":
            b = tk.Button(self.page, text=region + plotname)
            b.grid(row=0, column=0, rowspan=7, columnspan=2, sticky="NSEW")
        elif region == "bottom":
            b = tk.Button(self.page, text=region + plotname)
            b.grid(row=7, column=0, rowspan=7, columnspan=2, sticky="NSEW")
        elif (len(region) == 3) and (region[0] == "r"):
            # Make sure region is valid
            # rAB: A and B must be ints
            try:
                r = int(region[1])
                rmax = int(region[2])
            except ValueError:
                return
            # A <= B, A and B between 1 and 4
            if (r not in range(1, 5)) or (r not in range(1, 5)) or (r > rmax):
                return
            # Convert to 0 index
            r = r - 1
            b = tk.Button(self.page, text=region + plotname)
            b.grid(
                row=int(r * 12 / rmax),
                column=0,
                rowspan=int(12 / rmax),
                columnspan=2,
                sticky="NSEW",
            )
        elif (len(region) == 5) and (region[0] == "r"):
            # Make sure region is valid
            # rABCD: A, B, C, D must be ints
            try:
                c = 3 - int(region[1])
                r = int(region[3])
                rmax = int(region[4])
            except ValueError:
                return
            # C<=D, A=1 or 2,  C and D between 1 and 4
            if (
                (c not in [1, 2])
                or (r not in range(1, 5))
                or (r not in range(1, 5))
                or (r > rmax)
            ):
                return
            # Convert to 0 index
            r = r - 1
            c = c - 1
            b = tk.Button(self.page, text=region + plotname)
            b.grid(
                row=int(r * 12 / rmax),
                column=c,
                rowspan=int(12 / rmax),
                columnspan=1,
                sticky="NSEW",
            )
        elif (len(region) >= 6) and (region[:6] == "layout"):
            if region[6:] == "":
                b = tk.Button(self.page, text=region + plotname)
                b.grid(row=12, column=0, rowspan=2, columnspan=2, sticky="NSEW")
            elif region[6:] == "1":
                b = tk.Button(self.page, text=region + plotname)
                b.grid(row=12, column=0, rowspan=2, columnspan=1, sticky="NSEW")
            elif region[6:] == "2":
                b = tk.Button(self.page, text=region + plotname)
                b.grid(row=12, column=1, rowspan=2, columnspan=1, sticky="NSEW")
        if b != 0:
            self.shown_regions[region] = b


# ------------------------------------------------------------------------------------
class tao_pgplot_config_window(Tao_Toplevel):
    """
    Provides a window for setting the pgplot window layout
    (number of rows/columns, number of lat_layouts, etc)
    """

    def __init__(self, root, pipe, *args, **kwargs):
        self.root = root
        self.tao_id = "plot"
        Tao_Toplevel.__init__(self, self.root, *args, **kwargs)
        self.title("PGPlot Settings")
        self.pipe = pipe
        self._refreshing = False  # prevent updating halfway through a refresh

        # Set up frames
        self.control_frame = tk.Frame(self)
        self.preview_frame = tk.Frame(self)
        self.bottom_frame = tk.Frame(self)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.control_frame.grid(row=0, column=0, sticky="NSEW")
        self.preview_frame.grid(row=0, column=1, sticky="NSEW")
        self.bottom_frame.grid(row=1, column=0, columnspan=2, sticky="NSEW")

        # Fill control frame
        glabel = tk.Label(self.control_frame, text="Plot area")
        glabel.grid(row=0, column=0, columnspan=2, sticky="EW")

        # rows
        rowlabel = tk.Label(self.control_frame, text="Rows:")
        rowlabel.grid(row=1, column=0, sticky="W")
        self.rowvar = tk.StringVar()
        rowlist = tk.OptionMenu(
            self.control_frame,
            self.rowvar,
            "1",
            "2",
            "3",
            "4",
            command=self.update_preview,
        )
        rowlist.grid(row=1, column=1, sticky="EW")

        # columns
        collabel = tk.Label(self.control_frame, text="Columns:")
        collabel.grid(row=2, column=0, sticky="W")
        self.colvar = tk.StringVar()
        collist = tk.OptionMenu(
            self.control_frame, self.colvar, "1", "2", command=self.update_preview
        )
        collist.grid(row=2, column=1, sticky="EW")

        # lat_layouts
        ttk.Separator(self.control_frame).grid(row=3, column=0, columnspan=2, sticky="EW")
        latlabel = tk.Label(self.control_frame, text="Lat_layout area")
        latlabel.grid(row=4, column=0, columnspan=2, sticky="W")
        latlabel1 = tk.Label(self.control_frame, text="Columns:")
        latlabel1.grid(row=5, column=0, sticky="W")
        self.latvar = tk.StringVar()
        latlist = tk.OptionMenu(
            self.control_frame, self.latvar, "0", "1", "2", command=self.update_preview
        )
        latlist.grid(row=5, column=1, sticky="EW")

        # Preview frame
        self.preview_frame.grid_rowconfigure(0, weight=0)
        self.preview_frame.grid_rowconfigure(1, weight=1)
        self.preview_frame.grid_columnconfigure(0, weight=1)
        plabel = tk.Label(self.preview_frame, text="Preview")
        plabel.grid(row=0, column=0, sticky="EW")
        self.pgpage = tao_pgplot_canvas(self.preview_frame, "config", self.root, self.pipe)
        self.pgpage.grid(row=1, column=0, sticky="NSEW")

        # Variable traces
        self.rowvar.trace("w", self.update_preview)
        self.colvar.trace("w", self.update_preview)
        self.latvar.trace("w", self.update_preview)

        self.refresh()

    def refresh(self, event=None):
        """
        Fetch the current settings for row, column, and lat_layout number
        and update rowvar, colvar, and latvar accordingly
        """
        self._refreshing = True
        self.rowvar.set(self.root.placed.pgplot_settings["rows"])
        self.colvar.set(self.root.placed.pgplot_settings["columns"])
        self.latvar.set(self.root.placed.pgplot_settings["lat_layouts"])
        self._refreshing = False
        self.update_preview()

    def update_preview(self, *args):
        """
        Draws rectangles to self.canvas to represent the pgplot
        window layout according to the values in self.rowvar,
        self.colvar, and self.latvar
        """
        if self._refreshing:
            return
        self.pgpage.rownum = int(self.rowvar.get())
        self.pgpage.colnum = int(self.colvar.get())
        self.pgpage.latnum = int(self.latvar.get())
        self.pgpage.refresh()


class tao_pgplot_place_window(Tao_Toplevel):
    """
    Provides a window that prompts the user for which
    pgplot region a new plot should be placed in,
    and then places the plot in the requested region.
    """

    def __init__(self, root, plot, pipe, *args, **kwargs):
        self.root = root
        Tao_Toplevel.__init__(self, root, *args, **kwargs)
        self.plot = plot
        self.region = ""
        self.pipe = pipe

        # Configure grid settings
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Region selector
        self.title("Place " + self.plot)
        title = tk.Label(self, text="Select region for " + self.plot + ":")
        title.grid(row=0, column=0, sticky="W")

        self.region_var = tk.StringVar()
        self.region_var.set("Select...")
        self.regions = self.pipe.cmd_in("python plot_list r").splitlines()
        for i in range(len(self.regions)):
            self.regions[i] = self.regions[i].split(";")[1]
        selector = tk.OptionMenu(
            self, self.region_var, *self.regions, command=self.update_region
        )
        selector.grid(row=0, column=1, sticky="EW")

        # Page display
        self.pgpage = tao_pgplot_canvas(self, "place", self.root, self.pipe)
        self.pgpage.grid(row=1, column=0, columnspan=2, sticky="NSEW")

        # Overlap warning
        self.overlap_warn = tk.Label(self, text="")
        self.warning_labels = []

        # Place button
        self.place_button = tk.Button(self, text="Place!", command=self.place_cmd)
        self.place_button.grid(row=2, column=0, columnspan=2, sticky="EW")

    def update_region(self, event=None):
        """
        Updates the pgpage widget to display the plot
        as it would be placed in the selected region,
        and warns the user if placing the plot in that region
        would cause other plots to be unplaced
        """
        # Clear warning labels that might already be present
        self.overlap_warn.grid_forget()
        for label in self.warning_labels:
            label.grid_forget()
        self.warning_labels = []
        # Update pgpage and get overlapping regions
        self.region = "" if (self.region_var.get() == "Select...") else self.region_var.get()
        self.pgpage.place_region = self.region
        self.pgpage.place_plot = self.plot
        overlapping = self.pgpage.refresh()
        # Warn the user if there are overlaps
        i = 2
        if overlapping != []:
            self.overlap_warn.configure(
                text="Warning: placing "
                + self.plot
                + " in the region "
                + self.region
                + "\nwill unplace the following plots:"
            )
            self.overlap_warn.grid(row=i, column=0, columnspan=2, sticky="W")
            i += 1
            for plot in overlapping:
                label = tk.Label(self, text="* " + plot[1] + " in region " + plot[0])
                label.grid(row=i, column=0, columnspan=2, sticky="W")
                self.warning_labels.append(label)
                i = i + 1
        # Reposition the place button
        self.place_button.grid(row=i, column=0, columnspan=2, sticky="EW")

    def place_cmd(self, event=None):
        """
        Places self.plot in the selected region and closes this window
        """
        # Make sure a region has been selected
        if self.region == "":
            return
        # Place the plot and close this window
        self.pipe.cmd_in("place -no_buffer " + self.region + " " + self.plot)
        self.destroy()


class tao_ele_shape_window(Tao_Toplevel):
    """
    Provides a window for holding an ele_shape_frame,
    which allows the user to view and edit the ele shapes
    for floor plan and lat_layout plots

    pipe: the tao_interface used to querry/set ele shapes
    which: either "lat_layout" or "floor_plan"
    """

    def __init__(self, root, pipe, which, *args, **kwargs):
        if which not in ["lat_layout", "floor_plan"]:
            raise ValueError('which must be "lat_layout" or "floor_plan"')
        self.root = root
        self.tao_id = "Plot"
        Tao_Toplevel.__init__(self, root, *args, **kwargs)
        self.title(which + " Shape Settings")
        self.pipe = pipe
        self.ele_frame = ele_shape_frame(self, root, pipe, which)
        self.ele_frame.pack(fill="both", expand=1)

    def refresh(self, event=None):
        self.ele_frame.refresh()


class tao_building_wall_window(Tao_Toplevel):
    """
    Provides a window for viewing and editing building_wall
    settings.

    pipe: the tao_interface used to querry/set ele shapes
    """

    def __init__(self, root, pipe, *args, **kwargs):
        self.root = root
        self.tao_id = "Plot"
        Tao_Toplevel.__init__(self, root, *args, **kwargs)
        self.title("Building Wall Settings")
        self.pipe = pipe
        self.table_frame = tk.Frame(self)
        self.table_frame.pack(fill="both", expand=1)
        self.button_frame = tk.Frame(self)
        self.button_frame.pack(fill="x", expand=0)

        self.refresh()

        # Fill the button frame
        for i in range(3):
            self.button_frame.grid_columnconfigure(i, weight=1)
        for i in range(2):
            self.button_frame.grid_rowconfigure(i, weight=1)

        tk.Button(self.button_frame, text="Add section", command=self.add_section).grid(
            row=0, column=0, sticky="EW"
        )
        tk.Button(self.button_frame, text="Add point", command=self.add_point).grid(
            row=1, column=0, sticky="EW"
        )
        tk.Button(
            self.button_frame,
            text="Delete selected section",
            command=self.delete_section,
        ).grid(row=0, column=1, sticky="EW")
        tk.Button(
            self.button_frame, text="Delete selected point", command=self.delete_point
        ).grid(row=1, column=1, sticky="EW")
        tk.Button(
            self.button_frame,
            text="Default floor_plan settings",
            command=self.floor_plan_default,
        ).grid(row=0, column=2, sticky="EW")
        tk.Button(
            self.button_frame,
            text="Floor_plan settings for selected section",
            command=self.floor_plan_selected,
        ).grid(row=1, column=2, sticky="EW")

    def refresh(self, event=None):
        """
        Redraws the table of wall sections with updated settings from tao
        """
        for child in self.table_frame.winfo_children():
            child.destroy()
        # Create the building wall table
        cols = ["Name", "Constraint", "Custom floor_plan settings?"]
        self.table = ttk.Treeview(self.table_frame, columns=cols)
        self.table.heading("#0", text="Section/Point")
        self.table.column("#0", stretch=True, anchor="center")
        for c in cols:
            self.table.heading(c, text=c)
            self.table.column(c, stretch=True, anchor="center")
        # Get building wall data from tao
        section_list = self.pipe.cmd_in("python building_wall_list").splitlines()
        floor_plan_list = self.pipe.cmd_in("python shape_list floor_plan").splitlines()
        for i in range(len(floor_plan_list)):
            floor_plan_list[i] = floor_plan_list[i].split(";")
        # Fill with sections and points
        for sec in section_list:
            sec = sec.split(";")
            # Determine whether or not this section
            # has specialized floor_plan settings
            sec.append("F")
            for shape in floor_plan_list:
                if shape[1] == "building_wall::" + sec[0]:
                    sec[3] = "T"
                    break
            current_level = self.table.insert(
                "", "end", text="Section " + str(sec[0]), values=sec[1:]
            )
            # Add points for this section
            points = self.pipe.cmd_in("python building_wall_list " + sec[0]).splitlines()
            for pt in points:
                self.table.insert(
                    current_level,
                    "end",
                    text="Point " + pt.split(";")[0],
                    values=["", "", ""],
                )
        self.table.pack(fill="both", expand=1)

    def get_selected(self, event=None):
        """
        Returns the selected row in the table, for
        use with other methods like add_point, etc.
        """
        x = self.table.focus()
        # row = self.table.item(x)
        # p = self.table.parent(x)
        # print(row)
        return x

    def add_section(self, event=None):
        """
        Adds an empty building wall section
        """
        row = self.get_selected()
        # Add section below the selected section
        if row != "":  # if a row is selected
            if self.table.parent(row) == "":
                # if a section is selected
                section = row
            else:  # if a point is selected
                section = self.table.parent(row)
            section_name = self.table.item(section, option="text")
            new_ix = int(section_name.split(" ")[1]) + 1
        else:  # if nothing is selected -> add section at end
            new_ix = len(self.table.get_children()) + 1

        # Open a window to specify name and constraint type
        win = Tao_Popup(self, self.root)
        win.title("New Building Wall Section")
        tk.Label(win, text="Name (optional):").grid(row=0, column=0, sticky="W")
        name_var = tk.StringVar()
        tk.Entry(win, textvariable=name_var).grid(row=0, column=1, sticky="EW")
        tk.Label(win, text="Constraint type").grid(row=1, column=0, sticky="W")
        constraint_var = tk.StringVar()
        tk.OptionMenu(win, constraint_var, "None", "Left side", "Right side").grid(
            row=1, column=1, sticky="EW"
        )
        constraint_var.set("None")

        def create(event=None):
            """Create the new section"""
            name = name_var.get()
            constraint = constraint_var.get().lower()
            constraint = constraint.replace(" ", "_")
            self.pipe.cmd_in(
                "python building_wall_section " + str(new_ix) + "^^" + name + "^^" + constraint
            )
            win.destroy()
            self.refresh()

        tk.Button(win, text="Create", command=create).grid(
            row=2, column=0, columnspan=2, sticky="EW"
        )

    def add_point(self, event=None):
        """
        Adds a point to the selected building wall section
        """
        row = self.get_selected()
        # Add point to the current section
        if row != "":  # if a row is selected
            if self.table.parent(row) == "":
                # if a section is selected -> put at end
                section = row
                point_ix = len(self.table.get_children(row)) + 1
            else:  # if a point is selected -> put new point after
                section = self.table.parent(row)
                point_name = self.table.item(row, option="text")
                point_ix = int(point_name.split(" ")[1]) + 1
            section_name = self.table.item(section, option="text")
            section_ix = int(section_name.split(" ")[1]) + 1
        else:  # if nothing is selected -> do nothing
            return

        # Open a window to specify name and constraint type
        win = Tao_Popup(self, self.root)
        win.title("New Building Wall Point")
        # tk.Label(win, text="Name (optional):").grid(row=0, column=0, sticky='W')
        # name_var = tk.StringVar()
        # tk.Entry(win, textvariable=name_var).grid(row=0, column=1, sticky='EW')
        # tk.Label(win, text="Constraint type").grid(row=1, column=0, sticky='W')
        # constraint_var = tk.StringVar()
        # tk.OptionMenu(win, constraint_var, "None", "Left side", "Right side").grid(
        #        row=1, column=1, sticky='EW')
        # constraint_var.set("None")

        def create(event=None):
            """Create the new section"""
            self.pipe.cmd_in(
                "python building_wall_point " + str(section_ix) + "^^" + str(point_ix)
                # TODO: this is broken
                # + "^^"
                # + name
                # + "^^"
                # + constraint
            )
            win.destroy()
            self.refresh()

        tk.Button(win, text="Create", command=create).grid(
            row=2, column=0, columnspan=2, sticky="EW"
        )

    def delete_section(self, event=None):
        """
        Deletes the selected building wall section
        """
        pass

    def delete_point(self, event=None):
        """
        Deletes the selected building wall point
        """
        pass

    def floor_plan_default(self, event=None):
        """
        Opens a window for editing the floor_plan shape
        building_wall::*
        """
        pass

    def floor_plan_selected(self, event=None):
        """
        Opens a window for editing the floor_plan shape
        building_wall::name, where name is the name of the
        selected building wall section
        """
        pass


class building_wall_point_window(Tao_Popup):
    """
    Window for specifying building wall point properties.
    Handles both creating new points and editing existing points.

    parent: the parent window for this window
    root:       the tao root window
    pipe:       tao_interface object
    section_ix: the 1-based building wall section index that
                this point belongs to
    point_ix:   the 1-based index of the point to be edited
    is_new:     specifies whether or not this should be a
                new point or an existing point should be edited
    """

    def __init__(self, parent, root, pipe, section_ix, point_ix, is_new):
        Tao_Popup.__init__(self, parent, root)
        self.pipe = pipe
        self.section_ix = section_ix
        self.point_ix = point_ix
        self.is_new = is_new
