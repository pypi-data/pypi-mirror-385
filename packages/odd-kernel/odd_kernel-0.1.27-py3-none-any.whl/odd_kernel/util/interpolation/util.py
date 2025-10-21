import numpy as np

def add_padding(x, y, padding):
    amplitude = np.abs(y-x)
    return x - padding*amplitude, y + padding*amplitude