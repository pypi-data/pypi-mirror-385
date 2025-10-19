import numpy as np

def rotationVectU(u_vect: np.array, angle: float):
    """
    Create the rotation matrix around an axis defined by the input vector `u_vect` by a specified angle.
    This function computes the rotation matrix for a given axis and angle using the 
    Rodrigues' rotation formula and returns the resulting rotation matrix.
    Parameters:
    -----------
    u_vect : np.array
        A 3D input vector [ux, uy, uz] that defines the axis of rotation.
        It should be a numpy array.
    angle : float
        The rotation angle in radians.
    Returns:
    --------
    np.array
        A 3x3 rotation matrix that can be used to rotate vectors around the axis defined by `u_vect`.
    Notes:
    ------
    - The input vector `u_vect` should ideally be a unit vector. If it is not normalized, 
      the resulting rotation matrix may not behave as expected.
    - The function does not perform the actual rotation of a vector; it only returns the 
      rotation matrix.

    """
    
    cos_ang = np.cos(angle)
    sin_ang = np.sin(angle)
    ux = u_vect[0]
    uy = u_vect[1]
    uz = u_vect[2]

    rot = np.zeros([3,3])
    rot[:,:] = [[(cos_ang + ux ** 2 * (1 - cos_ang)), (ux * uy * (1 - cos_ang) - uz * sin_ang),
            (ux * uz * (1 - cos_ang) + uy * sin_ang)],
           [(uy * ux * (1 - cos_ang) + uz * sin_ang), (cos_ang + uy ** 2 * (1 - cos_ang)),
            (uy * uz * (1 - cos_ang) - ux * sin_ang)],
           [(uz * ux * (1 - cos_ang) - uy * sin_ang), (uz * uy * (1 - cos_ang) + ux * sin_ang),
            (cos_ang + uz ** 2 * (1 - cos_ang))]]

    return rot