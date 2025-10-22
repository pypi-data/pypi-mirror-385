import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsRegressor
from .util import add_padding

def knn_interpolate(x_p, y_p, X, n_neighbors=5, weights="distance", return_neighbors=False):
    """
    Interpolate values using KNeighborsRegressor with normalized coordinates via Pipeline.

    Parameters
    ----------
    x_p : ndarray of shape (n_samples, n_features)
        Known coordinates.
    y_p : ndarray of shape (n_samples,)
        Known values.
    X : ndarray of shape (m_samples, n_features) 
        Query coordinates.
    n_neighbors : int
        Number of neighbors.
    weights : str or callable
        Weighting strategy.
    return_neighbors : bool
        If to return additionally the neighbors used in the estimation.

    Returns
    -------
    y : ndarray of shape (m_samples,)
        Interpolated values.
    """
    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("knn", KNeighborsRegressor(n_neighbors=n_neighbors, weights=weights))
    ])

    pipeline.fit(x_p, y_p)
    result = pipeline.predict(X)

    if return_neighbors:
        assert len(X) == 1, "Return neighbors only available for single sample"
        x_scaled = pipeline.named_steps["scaler"].transform(X)
        _, indices = pipeline.named_steps["knn"].kneighbors(x_scaled)
        return result, indices
    else:
        return result

def knn_interpolate_mesh(x_p, y_p, z_p, mesh_size, k=5, padding=0.1):
    """
    Interpolates scattered 3D data onto a regular 2D grid using KNeighborsRegressor.

    Parameters
    ----------
    x_p : array-like of shape (n_samples,)
        X-coordinates of the input points.

    y_p : array-like of shape (n_samples,)
        Y-coordinates of the input points.

    z_p : array-like of shape (n_samples,)
        Z-values corresponding to each (x_p, y_p) point.

    mesh_size : int
        Number of grid points along each axis in the output mesh.

    k : int, optional, default=5
        Number of nearest neighbors to use for interpolation.

    padding : float, optional, default=0.1
        Fraction of the total data range to add as padding on each axis.

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
        Interpolated Z-values on the (X, Y) grid.
    """

    x_l, x_r = add_padding(np.min(x_p), np.max(x_p), padding)
    y_l, y_r = add_padding(np.min(y_p), np.max(y_p), padding)

    x = np.linspace(x_l, x_r, mesh_size)
    y = np.linspace(y_l, y_r, mesh_size)
    X, Y = np.meshgrid(x, y)

    # Input data
    points = np.column_stack((x_p, y_p))
    
    # KNN model
    knn = KNeighborsRegressor(n_neighbors=k, weights='distance')
    knn.fit(points, z_p)

    # Predict on mesh
    grid_points = np.column_stack((X.ravel(), Y.ravel()))
    Z = knn.predict(grid_points).reshape(mesh_size, mesh_size)

    return x, y, X, Y, Z
