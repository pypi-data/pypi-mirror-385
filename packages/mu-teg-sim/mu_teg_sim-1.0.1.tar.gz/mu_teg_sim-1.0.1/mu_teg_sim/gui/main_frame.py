import tkinter as tk
from mu_teg_sim.gui.input_frame import InputFrame
from mu_teg_sim.gui.simulation_frame import SimulationFrame
from mu_teg_sim.gui.status_bar_frame import StatusBarFrame
from mu_teg_sim.model.model_params import ModelParams


class MainFrame(tk.Tk):
    """ A class for the MainFrame GUI. Inherits from tk.Frame.
    Once instantiated, the class starts a GUI. """

    def __init__(self, width=1150, height=800):
        super().__init__()
        self.title("muTEG Simulator")
        self.geometry(f"{width}x{height}")
        self.minsize(width, height)

        # Add model and model parameters
        self.model_params = ModelParams(root=self)

        # Add Widgets
        self.frame_input = InputFrame(self)
        self.frame_output = SimulationFrame(self)
        self.frame_status_bar = StatusBarFrame(self)
