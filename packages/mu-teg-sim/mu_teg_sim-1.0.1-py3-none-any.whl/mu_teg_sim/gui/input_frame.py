import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog
from mu_teg_sim.utils.tk_variables import tk_var_converter
import json


class InputFrame(tk.Frame):
    """ A class for Input Frame with EntryLine widgets. Inherits from tk.Frame. """

    def __init__(self, main_frame):
        super().__init__(main_frame)
        self.main_frame = main_frame
        self._build_input_frame()
        self.place(relx=0, rely=0, relwidth=0.3, relheight=0.95)

    def _build_input_frame(self):
        # Add buttons for loading and saving model data
        frame_buttons = tk.Frame(master=self, pady=5)
        tk.Button(master=frame_buttons, text="Reset", command=self._event_button_reset).pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        tk.Button(master=frame_buttons, text="Load Params", command=self._event_button_load).pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        tk.Button(master=frame_buttons, text="Save Params", command=self._event_button_save).pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        frame_buttons.pack()

        # Create tabs
        notebook = ttk.Notebook(master=self)

        # Add EntryLine widgets to Tab1: "Physical Properties" and "Device Design"
        tab1 = tk.Frame(master=notebook)
        frame1 = tk.Frame(master=tab1)
        for block in list(self.main_frame.model_params.params.keys())[0:2]:
            tk.Label(master=frame1, text=block).pack(expand=True, fill=tk.BOTH, padx=1)
            for param in self.main_frame.model_params.params[block].keys():
                EntryLine(master=frame1, label=param, param=self.main_frame.model_params.params[block][param]).pack(side=tk.TOP)
        frame1.pack()

        # Add EntryLine widgets to Tab2: "Solver Parameters" and "Initial Condition"
        tab2 = tk.Frame(master=notebook)
        frame2 = tk.Frame(master=tab2)
        for block in list(self.main_frame.model_params.params.keys())[2:]:
            tk.Label(master=frame2, text=block).pack(expand=True, fill=tk.X, padx=1)
            for param in self.main_frame.model_params.params[block].keys():
                EntryLine(master=frame2, label=param, param=self.main_frame.model_params.params[block][param]).pack(side=tk.TOP)
        frame2.pack()

        # Pack tabs
        notebook.add(tab1, text="Model Params")
        notebook.add(tab2, text="Simulation Params")
        notebook.pack(expand=False, fill=tk.X, side=tk.TOP)

    def _event_button_reset(self):
        """ Reset all model parameters to their default value. """
        self.main_frame.model_params.init_current_values()

    def _event_button_load(self):
        """ Load and set model params from .json file on disc.
        Note: the method overwrites the 'current values', only if loaded params passes validation. """
        file_path = tkinter.filedialog.askopenfilename(initialdir="/", title="Select a file")
        if not file_path:
            self.main_frame.frame_status_bar.text.set(value=f"Attention! Params not loaded.")
            return
        self._load_params_from_json_file_on_disc(file_path=file_path)

    def _event_button_save(self):
        """ Save model parameters to disc in .json format. Note: it saves only the 'current values'. """
        data_to_save = self.main_frame.model_params.convert_params_to_json_compatible_format()
        file_path = tkinter.filedialog.asksaveasfilename(initialdir="/", title="Save Data As", filetypes=(("Json files", "*.json"), ("All files", "*.*")), defaultextension=".json")
        if not file_path:
            self.main_frame.frame_status_bar.text.set(value=f"Attention! Params not saved.")
            return
        self._save_params_to_json_file_on_disc(file_path=file_path, data_to_save=data_to_save)

    def _save_params_to_json_file_on_disc(self, file_path: str, data_to_save: dict):
        """ Save data to 'file_path' on disc. """
        try:
            with open(file_path, 'w') as file:
                json.dump(data_to_save, file, indent=4)
        except (OSError, TypeError) as e:
            self.main_frame.frame_status_bar.text.set(value=f"Attention! Data not saved. Error: {e}")
            return
        self.main_frame.frame_status_bar.text.set(value=f"Params saved to {file_path}.")

    def _load_params_from_json_file_on_disc(self, file_path: str):
        """ Validate parameters in loaded file
        Note: this is different from validating current values against default values within param object"""
        try:
            with open(file_path, "r") as file:
                params_to_load = json.load(file)
        except (TypeError, AttributeError, UnicodeError):
            self.main_frame.frame_status_bar.text.set(f"Error loading file '{file_path}'.")
            return

        # Check if parameter exists, is of correct type, and within range
        for block in self.main_frame.model_params.params.keys():
            for param in self.main_frame.model_params.params[block].keys():
                if param not in params_to_load[block]:
                    self.main_frame.frame_status_bar.text.set(value=f"File '{file_path}' corrupted! Param '{param}' is missing.")
                    return

                # Check data type
                try:
                    datatype = tk_var_converter(var=self.main_frame.model_params.params[block][param].current_value)
                    datatype(params_to_load[block][param])
                except (TypeError, ValueError):
                    self.main_frame.frame_status_bar.text.set(
                        value=f"File '{file_path}' corrupted! Param '{param}' is type '{type(param)}' but must be type "
                              f"'{tk_var_converter(var=self.main_frame.model_params.params[block][param].current_value)}'.")
                    return

                # Check interval
                if not self.main_frame.model_params.params[block][param].get_interval()[0] <= params_to_load[block][param] <= \
                       self.main_frame.model_params.params[block][param].get_interval()[1]:
                    self.main_frame.frame_status_bar.text.set(value=f"File '{file_path}' corrupted! Param '{param}' is out of range.")
                    return

        # Load parameters
        for block in self.main_frame.model_params.params.keys():
            for param in self.main_frame.model_params.params[block].keys():
                self.main_frame.model_params.params[block][param].set_current_value(value=params_to_load[block][param])
        self.main_frame.frame_status_bar.text.set(value=f"Params successfully loaded from '{file_path}'.")


class EntryLine(tk.Frame):
    """ A class to define the EntryLine Widget: [label: str][value: tk.Var][units: str]"""

    def __init__(self, master, label, param):
        super().__init__(master)

        # Add parameter label
        tk.Label(master=self, text=label, anchor=tk.N, width=7).pack(side=tk.LEFT)

        # Add entry and configure validate command and invalid function. Note: configure must come after defining vcmd and icmd.
        self.entry = tk.Entry(master=self, textvariable=param.current_value, width=15)
        vcmd = self.register(lambda x: self.on_valid(param))
        icmd = self.register(lambda: self.on_invalid())
        self.entry.config(validate="focusout", validatecommand=(vcmd, '%P'), invalidcommand=icmd)
        self.entry.pack(side=tk.LEFT)

        # Add units label
        tk.Label(master=self, text=param.get_units(), anchor=tk.W, width=10).pack(side=tk.LEFT)

    def on_valid(self, param):
        """ If entry is valid, set entry background color to default, i.e. white. """
        if param.validate():
            self.entry.config(bg="white")
            return True
        else:
            return False

    def on_invalid(self):
        """ If entry is not valid, set entry background color to red. """
        self.entry.config(bg="red")
