import numpy as np
from matplotlib.pyplot import cm

def get_colors(size):
    return cm.rainbow(np.linspace(0, 1, size))