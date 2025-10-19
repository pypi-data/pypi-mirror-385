from decimal import Decimal, getcontext
from typing import Union

import numpy as np
import sympy as spy

from optical_ray_tracer.configurations.main import Geometry
from optical_ray_tracer.utils.rotation_vect import rotationVectU
from optical_ray_tracer.rays.source.main import RaySource

getcontext().prec = 80

class GivenGeometry(Geometry):

    def __init__(self, rotation_angle, equation: str):

        super().__init__(rotation_angle)
        self.edge_tol = 1e-3
        self.string_equation = equation
        # Rotation matrix around x axis
        self.rot_x = rotationVectU(np.array([1, 0, 0]), self.rotation_angle)

    def symbolic_equation(self):
        # Convert the equation string to a sympy expression
        x_m, y_m, z_m = spy.symbols('x y z')
        u = spy.Matrix([x_m, y_m, z_m])
        rot = spy.Matrix(self.rot_x)
        u_rot = rot * u
        try:
            # Create the sympy expression from the string
            expr = spy.sympify(self.string_equation)
            # Check that the expression only uses x, y, z as variables
            if not all(str(sym) in ['x', 'y', 'z'] for sym in expr.free_symbols):
                raise ValueError("L'équation ne doit contenir que les variables x, y, z")
            # Create the sympy function with the class symbols
            func = expr.subs({'x': u_rot[0], 'y': u_rot[1], 'z': u_rot[2]})
        except spy.SympifyError as exc:
            raise ValueError("The given equation is not a valid mathematical expression") from exc
        
        return func
    
    def boundaries(self, x_min: float, x_max: float, y_min: float, y_max: float, z_min: float, z_max: float):
        """
        Defines the boundaries of a 3D geometry in terms of minimum and maximum 
        values along the x, y, and z axes.
        Args:
            x_min (float): The minimum value along the x-axis.
            x_max (float): The maximum value along the x-axis.
            y_min (float): The minimum value along the y-axis.
            y_max (float): The maximum value along the y-axis.
            z_min (float): The minimum value along the z-axis.
            z_max (float): The maximum value along the z-axis.
        Returns:
            list[list[float]]: A nested list containing the minimum and maximum 
            values for each axis in the format [[x_min, x_max], [y_min, y_max], [z_min, z_max]].
        """
        
        return [[x_min, x_max], [y_min, y_max], [z_min, z_max]]


    def arbitrary_volume(self, bounds: list[list[float]]):
        """
        Compute the isosurface volume points of the reflector within the specified boundaries.
        This method calculates the volume of the isosurface defined by the reflector's equation.
        It evaluates the equation over a 3D grid of points within the boundaries and applies a rotation
        transformation to determine the valid points. Points outside the height limit are excluded.
        Returns:
            numpy.ndarray: A 3D array representing the isosurface volume, where values close to zero
            correspond to the isosurface points.
        Notes:
            - The method uses symbolic computation to define the equation and evaluates it
              numerically over the grid.
            - The rotation transformation is applied to align the points with the reflector's orientation.
            - Debugging information about the volume shape and the number of isosurface points can be printed.
        """

        x, y, z = spy.symbols('x y z')
        equ = spy.lambdify((x, y, z), self.symbolic_equation(), 'numpy')
        nb_pts = 20
        xx, yy, zz = np.meshgrid(np.linspace(bounds[0][0], bounds[0][1], nb_pts),
                                 np.linspace(bounds[1][0], bounds[1][1], nb_pts),
                                 np.linspace(bounds[2][0], bounds[2][1], nb_pts),
                                 indexing='ij')
        values = equ(xx, yy, zz)
        z_rot = np.zeros(xx.shape)
        for ii in np.arange(nb_pts):
            for jj in np.arange(nb_pts):
                for kk in np.arange(nb_pts):
                    z_rot[ii, jj, kk] = np.dot(self.rot_x,
                                               (xx[ii, jj, kk], yy[ii, jj, kk], zz[ii, jj, kk]))[2]

        # values[z_rot >= self.h] = 0.1

        return values
    
    
    def generate_arbitrary_rays_from_source(self, theta_phi: list[float], source: RaySource):

        vec_dir = []
        pt_orig = []
        for theta_val, phi_val in theta_phi: # type: ignore
            v, p = source.rays(theta=theta_val, phi=phi_val)
            vec_dir += v
            pt_orig += p

        return vec_dir, pt_orig
    