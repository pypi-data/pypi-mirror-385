from optical_ray_tracer.rays.source.main import RaySource
from optical_ray_tracer.utils.sphericalcartesian import sphericalcartesian as vec_dir
import numpy as np
from typing import Union
from decimal import getcontext
getcontext().prec = 80

class Source(RaySource):
    
    def __init__(self, position_x, position_y, position_z, source_extent=0.0):

        super().__init__(position_x=position_x, position_y=position_y, position_z=position_z)
        self.x = position_x
        self.y = position_y
        self.z = position_z
        self.source_extent = source_extent
        self.pt_origin = [self.x, self.y, self.z]

    def rays(self, theta:Union[float, np.ndarray], phi:Union[float, np.ndarray]):
        
        """
        Generates direction vectors and origin points for rays based on input angles.

        Parameters:
            theta (Union[float, np.ndarray]): The polar angle(s) in radians. Can be a single float or a NumPy array of floats.
            phi (Union[float, np.ndarray]): The azimuthal angle(s) in radians. Can be a single float or a NumPy array of floats.

        Returns:
            Tuple:
                - u_dir (list or object): List of direction vectors (if theta or phi are arrays) or a single direction vector (if both are floats), computed using the `vec_dir` function.
                - pt_o (list or object): List of origin points (if theta or phi are arrays) or a single origin point (if both are floats), corresponding to the direction vectors.

        Notes:
            - If either `theta` or `phi` is an array, the function computes the Cartesian product of all combinations of `theta` and `phi`, returning lists of direction vectors and origin points.
            - If both `theta` and `phi` are floats, returns a single direction vector and origin point.
        """

        if isinstance(theta, np.ndarray) or isinstance(phi, np.ndarray):
            tuple_val = [(t,p) for t in theta for p in phi]
            u_dir = list(map(vec_dir, tuple_val))
            pt_o = [self.pt_origin for i in range(len(tuple_val))]
        else:
            u_dir = vec_dir([theta, phi])
            pt_o = self.pt_origin

        return u_dir, pt_o