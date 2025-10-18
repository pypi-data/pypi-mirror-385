import tkinter as tk


class StatusBarFrame(tk.Frame):
    def __init__(self, main_frame):
        super().__init__(main_frame)
        self.text = tk.StringVar(value="Waiting for user input... ")
        self._create_layout()
        self.place(relx=0, rely=0.95, relwidth=1, relheight=0.05)

    def _create_layout(self):
        """ Create SatusBarFrame's layout. """
        self.label_credits = tk.Label(self, text="GNU License. Credits @Davide Beretta")
        self.label_credits.place(relx=0, rely=0, relwidth=0.3, relheight=1)
        self.label_info = tk.Label(self, textvariable=self.text)
        self.label_info.place(relx=0.3, rely=0, relwidth=0.7, relheight=1)
