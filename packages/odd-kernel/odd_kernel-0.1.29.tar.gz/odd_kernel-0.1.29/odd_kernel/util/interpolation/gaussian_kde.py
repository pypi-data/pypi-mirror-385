import numpy as np
from .util import add_padding

def gaussian_kde_interpolate(x_p, y_p, x, h=None, eps=1e-9):
    """
    Multidimensional Gaussian KDE interpolation with per-dimension normalization.
    If no bandwidth (h) is provided, it defaults to the average spacing of the 
    evaluation grid along each dimension.

    Parameters
    ----------
    x_p : array_like, shape (n, d)
        Sample points (coordinates).
    y_p : array_like, shape (n,)
        Values associated with the sample points.
    x : array_like, shape (..., d)
        Evaluation points. The last dimension must be d.
        Example: for a 2D meshgrid, shape is (nx, ny, 2).
    h : None, float or array_like of shape (d,), optional
        Bandwidth. 
        - If None: uses the average spacing of the evaluation grid per dimension.
        - If float: the same bandwidth is used for all dimensions.
        - If array_like: interpreted as per-dimension bandwidth.
    eps : float
        Small value to avoid division by zero.

    Returns
    -------
    y : ndarray, shape (...,)
        Interpolated values with the same shape as x without the last dimension.
    """
    x_p = np.asarray(x_p, dtype=float)
    y_p = np.asarray(y_p, dtype=float)
    x = np.asarray(x, dtype=float)

    if x_p.ndim != 2:
        raise ValueError("x_p must have shape (n, d)")
    if x.shape[-1] != x_p.shape[1]:
        raise ValueError("The last dimension of x must equal d")

    n, d = x_p.shape

    # Bandwidth selection
    if h is None:
        h_per_dim = []
        for j in range(d):
            coords = np.unique(x[..., j].ravel())
            if len(coords) > 1:
                spacing = np.mean(np.diff(np.sort(coords)))
            else:
                spacing = 1.0  # fallback if only one coordinate
            h_per_dim.append(spacing)
        h_per_dim = np.array(h_per_dim)
    else:
        if np.isscalar(h):
            h_per_dim = np.full(d, float(h))
        else:
            h_per_dim = np.asarray(h, dtype=float)
            if h_per_dim.shape != (d,):
                raise ValueError(f"h must be scalar or of shape ({d},,)")

    h_per_dim = np.maximum(h_per_dim, eps)

    # Mean of y for centered Nadaraya-Watson estimator
    y_mean = np.mean(y_p)

    # Output arrays
    out_shape = x.shape[:-1]
    y = np.zeros(out_shape, dtype=float)
    w = np.zeros(out_shape, dtype=float)

    # Accumulate weights and weighted values
    for i in range(n):
        dx = (x - x_p[i]) / h_per_dim   # normalize per dimension
        dist2 = np.sum(np.square(dx), axis=-1)
        weight = np.exp(-0.5 * dist2)
        w += weight
        y += (y_p[i] - y_mean) * weight

    mask = (w > 0)
    if np.any(mask):
        y[mask] /= w[mask]
    y += y_mean

    return y



def gaussian_kde_interpolate_mesh(x_p, y_p, z_p, mesh_size, padding = 0.1, h=None):
    """
    Perform Gaussian kernel density estimation (KDE) based interpolation of scattered 3D data 
    over a regular 2D grid.

    Parameters
    ----------
    x_p : array-like of shape (n_samples,)
        X-coordinates of the input data points.

    y_p : array-like of shape (n_samples,)
        Y-coordinates of the input data points.

    z_p : array-like of shape (n_samples,)
        Z-values (scalar field) corresponding to each (x_p, y_p) point.

    mesh_size : int
        Number of grid points along each axis in the output mesh.

    padding : float, optional, default=0.1
        Extra margin added to the data range in both X and Y directions. 
        Expressed as a fraction of the total range.

    h : float, optional, default=None
        Bandwidth (smoothing parameter) of the Gaussian kernel. 
        If None, it is estimated as half the mean grid spacing 
        (using both x and y axis resolutions).

    Returns
    -------
    x : ndarray of shape (mesh_size,)
        1D array containing the grid values along the X-axis.

    y : ndarray of shape (mesh_size,)
        1D array containing the grid values along the Y-axis.

    X : ndarray of shape (mesh_size, mesh_size)
        2D array containing the X-coordinates of the interpolation grid.

    Y : ndarray of shape (mesh_size, mesh_size)
        2D array containing the Y-coordinates of the interpolation grid.

    Z : ndarray of shape (mesh_size, mesh_size)
        Interpolated Z-values on the (X, Y) grid, smoothed using Gaussian weights.

    Notes
    -----
    - The interpolation is performed by weighting each input point (x_p[i], y_p[i]) 
      with a Gaussian kernel centered at that point.
    - The Z-values are normalized by the sum of weights to produce a smooth surface.
    - Adding padding prevents boundary effects and ensures that points near the edges 
      of the data are properly represented.
    - Compared to the previous version, the bandwidth `h` is chosen as the minimum 
      of the average grid spacings along X and Y, divided by 2.

    Examples
    --------
    >>> x = np.random.rand(50)
    >>> y = np.random.rand(50)
    >>> z = np.sin(x*10) + np.cos(y*10)
    >>> xg, yg, X, Y, Z = gaussian_kde_interpolate(x, y, z, mesh_size=100)
    """
    
    x_l, x_r = add_padding(np.min(x_p), np.max(x_p), padding)
    y_l, y_r = add_padding(np.min(y_p), np.max(y_p), padding)
    x = np.linspace(x_l, x_r, mesh_size)
    y = np.linspace(y_l, y_r, mesh_size)
    X, Y = np.meshgrid(x, y)

    if h is None:
        effective_h = min(np.mean(np.diff(x)), np.mean(np.diff(y))) / 2
    else:
        effective_h = h 

    z_mean = np.mean(z_p)
    Z = np.zeros_like(X)
    W = np.zeros_like(X)

    for i in range(len(x_p)):
        dx = X - x_p[i]
        dy = Y - y_p[i]
        weight = np.exp(-(dx*dx + dy*dy) / (2*effective_h*effective_h))
        W += weight
        Z += (z_p[i] - z_mean) * weight
    Z[W != 0.0] /= W[W != 0.0]
    Z += z_mean

    return x, y, X, Y, Z