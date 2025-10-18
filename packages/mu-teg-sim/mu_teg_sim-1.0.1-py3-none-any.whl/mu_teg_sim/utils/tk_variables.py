import tkinter as tk


def tk_var_converter(var):
    """ Given a Tkinter variable 'var', it returns the 'corresponding' python variable. """
    if isinstance(var, tk.StringVar):
        return str
    elif isinstance(var, tk.IntVar):
        return int
    elif isinstance(var, tk.DoubleVar):
        return float
    elif isinstance(var, tk.BooleanVar):
        return bool
    else:
        return None
