import numpy as np

def sphericalcartesian(theta_phi: list[float]):
    """
    Converts spherical coordinates (theta, phi) to Cartesian coordinates (x, y, z). 
    Assumes a unit radius.
    Args:
        theta_phi (list[float]): A list containing two elements: 
                                 - theta (float): The polar angle in radians, measured from the positive z-axis.
                                 - phi (float): The azimuthal angle in radians, measured from the positive x-axis in the x-y plane.
    Returns:
        list[float]: A list containing the Cartesian coordinates [x, y, z].
    """
    theta = np.float64(theta_phi[0])
    phi = np.float64(theta_phi[1])
    return [np.sin(theta) * np.cos(phi), np.sin(theta) * np.sin(phi), -np.cos(theta)]