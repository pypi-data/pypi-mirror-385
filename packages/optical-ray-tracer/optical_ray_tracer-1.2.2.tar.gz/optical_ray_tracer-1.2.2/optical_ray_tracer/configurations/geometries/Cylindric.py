from decimal import Decimal, getcontext

import numpy as np
import sympy as spy

from optical_ray_tracer.configurations.main import Geometry
from optical_ray_tracer.utils.rotation_vect import rotationVectU
from optical_ray_tracer.rays.source.main import RaySource

getcontext().prec = 80

class CylindricalReflector(Geometry):

    def __init__(self, length, height, thickness, rot_angle, orientation = [0, 1, 0], surf_pos=[0,0,0], edge_tol=1e-3):
        super().__init__(surf_pos, rot_angle, edge_tol)
        self.length = length
        self.height = height
        self.thickness = thickness - self.edge_tol # reduce a bit the thickness to avoid numerical issues
        # orientation of the cylinder revolution axis
        self.revol_axis = np.array(orientation) / (orientation[0]**2 + orientation[1]**2 + orientation[2]**2)**0.5
        self.rot = rotationVectU(orientation, self.rotation_angle)


    def symbolic_equation(self):
        """
        Computes the symbolic equation for a cylindrical geometry with an elliptical section.
        This method calculates a symbolic equation representing the geometry of a cylinder 
        with an elliptical cross-section. The cylinder's revolution axis, thickness, and height 
        are used to define the geometry. The equation is derived based on the distance of points 
        on the surface of the cylinder to its revolution axis.
        Returns:
            sympy.Expr: A simplified symbolic expression representing the equation of the cylinder.
        Notes:
            - The calculations assume the default revolution axis of the cylinder is (0, 1, 0).
            - The elliptical section parameters are defined by the major axis (thickness/2) and 
              the minor axis (height).
            - The function uses symbolic computation with sympy to derive the equation.
        """
        
        x, y, z = spy.symbols('x y z')
        u = spy.Matrix([x - self.geometry_position[0], y - self.geometry_position[1], z - self.geometry_position[2]])
        rot = spy.Matrix(self.rot)
        u_rot = rot*u
        mu_vec = u_rot - spy.Matrix(self.revol_axis)
        # cylinder elliptical section prameters (th is the major axis and h is the minor axis)
        # by default the calculations are made for a revolution axis of the cylinder is (0, 1, 0)
        th = self.thickness/2
        h = self.height
        temp = spy.sqrt(th**2-x**2)
        corde = spy.Matrix([x, 0, h/th*temp]) # default point coordinates on the elliptical section
        # distance from each point of the surface to the revolution axis is then
        d_len = spy.simplify( spy.sqrt(corde[0]**2 + corde[1]**2 + corde[2]**2) ) # type: ignore
        # Equation 
        a = u_rot.cross(mu_vec)
        a_norm = spy.sqrt(a[0]**2 + a[1]**2 + a[2]**2)
        b_norm = 1.0 # spy.sqrt(self.revol_axis[0]**2 + self.revol_axis[1]**2 + self.revol_axis[2]**2)
        
        func = spy.simplify( a_norm - d_len * b_norm )

        return func

    def boundaries(self):
        """
        Compute the boundaries of the cylindrical reflector in the rotated frame, considering the desired height 
        and dimensions of the reflector.
        The method calculates the minimum and maximum extents of the reflector in the y and z directions 
        after applying a rotation transformation. 
        Returns:
            list: A list of boundaries in the format [[xmin, xmax], [ymin, ymax], [zmin, zmax]], where:
                - xmin, xmax: The minimum and maximum x-coordinates after rotation.
                - ymin, ymax: The minimum and maximum y-coordinates after rotation.
                - zmin, zmax: The minimum and maximum z-coordinates after rotation.
        
        Compute the boundaries of the cylindrical reflector in the rotated frame taking in account the desired height of the reflector
        """
        rx = self.thickness/2
        ry = self.length/2

        # Compute the graphical extent after the rotation
        rot_lim_1 = np.dot(self.rot, np.array([-rx, 0, 0]))
        rot_lim_2 = np.dot(self.rot, np.array([rx, 0, 0]))
        rot_lim_3 = np.dot(self.rot, np.array([-rx, 0, self.height]))
        rot_lim_4 = np.dot(self.rot, np.array([rx, 0, self.height]))
        xl_min = np.min(np.array([-rot_lim_1[1], -rot_lim_2[1], -rot_lim_3[1], -rot_lim_4[1]]))
        xl_max = np.max(np.array([-rot_lim_1[1], -rot_lim_2[1], -rot_lim_3[1], -rot_lim_4[1]]))
        zl_min = np.min(np.array([rot_lim_1[2], rot_lim_2[2], rot_lim_3[2], rot_lim_4[2]]))
        zl_max = np.max(np.array([rot_lim_1[2], rot_lim_2[2], rot_lim_3[2], rot_lim_4[2]]))

        return [[-xl_min, xl_max], [-ry, ry], [zl_min, zl_max]]

    def volume(self):
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

        # Compute parabola surface equation
        x, y, z = spy.symbols('x y z')
        equ = self.symbolic_equation()
        parabola_equ = spy.lambdify((x, y, z), equ, 'numpy')
        bounds = self.boundaries()
        nb_pts = 20
        xx, yy, zz = np.meshgrid(np.linspace(bounds[0][0], bounds[0][1], nb_pts),
                                 np.linspace(bounds[1][0], bounds[1][1], nb_pts),
                                 np.linspace(bounds[2][0], bounds[2][1], nb_pts),
                                 indexing='ij')
        values = parabola_equ(xx, yy, zz)
        z_rot = np.zeros(xx.shape)
        for ii in np.arange(nb_pts):
            for jj in np.arange(nb_pts):
                for kk in np.arange(nb_pts):
                    z_rot[ii, jj, kk] = np.dot(self.rot,
                                               (xx[ii, jj, kk], yy[ii, jj, kk], zz[ii, jj, kk]))[2]

        values[z_rot >= self.height] = 0.1
        # print("Volume shape: ", values.shape)
        # print("IsoSurface nb of pts", np.size(np.where(np.abs(values)== 0.0)))

        return [values]

    def collection_area(self):
        """
        Calculate the collection area of the cylindrical geometry.
        The collection area is determined by the product of the cylinder's 
        length and thickness. Note that the angle of collection is not 
        considered in this calculation and may be included in future versions.
        Returns:
            float: The calculated collection area.
        """
        # we should consider the angle of collection in future versions...
        a = self.length * self.thickness
        
        return a

    def generate_rays_from_source(self, n_rays: int, source: RaySource):
        """
        Generate rays originating from a source within the bounds of the reflector geometry.
        This method generates a specified number of rays (`n_rays`) from a given source object.
        The rays are distributed based on the reflector aperture and are defined by their
        direction vectors and origin points.
        Args:
            n_rays (int): The total number of rays to generate. The rays are distributed
                          approximately evenly in a grid-like pattern.
            source (object): The source object that provides the origin points and direction
                             vectors for the rays. The source object must implement a `rays`
                             method that accepts `theta` and `phi` parameters.
        Returns:
            tuple: A tuple containing two lists:
                - vec_dir (list): A list of direction vectors for the generated rays.
                - pt_orig (list): A list of origin points for the generated rays.
        Notes:
            - The `source.rays` method is expected to return direction vectors and origin
              points for the specified `theta` and `phi` values.
        """

        phi_tab = np.linspace(0, 2 * np.pi, int(np.sqrt(n_rays)), endpoint=False)
        vec_dir = []
        pt_orig = []
        for val in phi_tab.tolist():
            # print("Origine = ", np.array(source.pt_origin))
            theta_lim = self.cylinder_aperture_theta_limit(val, np.array(source.pt_origin))
            theta_tab = np.linspace(theta_lim, 0, num=int(np.sqrt(n_rays)), endpoint=False)
            v, p = source.rays(theta=theta_tab, phi=val)
            vec_dir += v
            pt_orig += p

        return vec_dir, pt_orig

    @staticmethod
    def compute_material_surface(minor_axis: float, major_axis: float, length: float):
        """
        Compute the surface area of a cylindrical material.
        This function calculates the surface area of a cylindrical material 
        using the given minor axis, major axis, and length. The calculation 
        assumes an elliptical cross-section for the cylinder.
        Args:
            minor_axis (float): The minor axis of the elliptical cross-section.
            major_axis (float): The major axis of the elliptical cross-section.
            length (float): The length of the cylinder.
        Returns:
            float: The computed surface area of the cylindrical material.
        """
        a = np.pi * np.sqrt((minor_axis**2 + major_axis**2) / 2)
        area = a * length

        return area   

    def cylinder_aperture_rectangular_section(self, phi: float):
        """
        Calculates the 3D coordinates of a point on the aperture of a cylindrical geometry 
        with a rectangular cross-section, based on the given angle phi.
        Args:
            phi (float): The angle in radians, measured from the positive x-axis.
        Returns:
            numpy.ndarray: A 3D vector (numpy array) representing the coordinates [x, y, z] 
            of the point on the aperture.
        Notes:
            - The method assumes the cylinder has a rectangular cross-section.
            - The `phi` angle is used to determine the quadrant and the corresponding 
              coordinates on the aperture.
            - The `self.length`, `self.thickness`, and `self.height` attributes are used 
              to define the dimensions of the cylinder.
            - The thickness is reduced by 1e-3 to account for a small margin.
        """
        
        L = self.length
        d = self.thickness - 1e-3
        phi_1 = np.arctan(d/L)
        phi_2 = np.pi - phi_1
        phi_3 = np.pi + phi_1
        phi_4 = 2 * np.pi - phi_1
        vec = np.array([0, 0, 0])
        
        if (phi>=0.0) & (phi<=phi_1):
            vec = np.array([L/2 * np.tan(phi), L/2, self.height])
        elif (phi>phi_1) & (phi<=phi_2):
            vec = np.array([d/2, d / (2*np.tan(phi)), self.height])
        elif (phi>phi_2) & (phi<=phi_3):
            vec = np.array([-L/2 * np.tan(phi), -L/2, self.height])
        elif (phi>phi_3) & (phi<=phi_4):
            vec = np.array([-d/2, -d / (2*np.tan(phi)), self.height])
        elif phi>phi_4:
            vec = np.array([L/2 * np.tan(phi), L/2, self.height])
        
        return vec

    def cylinder_aperture_theta_limit(self, phi: float, pt_origin:np.ndarray):
        """
        Calculate the angular limit (theta) for a point on the cylindrical aperture 
        based on its position and orientation.
        This method computes the angular limit using the geometry of a cylinder 
        and the relative positions of the origin, a point on the cylinder, and 
        the given point of interest.
        Args:
            phi (float): The azimuthal angle (in radians) that defines the position 
                            on the cylindrical aperture's rectangular section.
            pt_origin (np.ndarray): A 3D numpy array representing the coordinates 
                                    of the origin point.
        Returns:
            Decimal: The calculated angular limit (theta) as a Decimal object.
        """

        O = np.dot(self.rot, np.array([0, 0, self.height]))
        M = self.cylinder_aperture_rectangular_section(phi)
        S = pt_origin
        OM = M-O
        # a = Decimal(OM[0]**2 + OM[1]**2 + OM[2]**2).sqrt()
        SO = O-S
        b = (Decimal(SO[0])**2 + Decimal(SO[1])**2 + Decimal(SO[2])**2).sqrt()
        SM = M-S
        c = (Decimal(SM[0])**2 + Decimal(SM[1])**2 + Decimal(SM[2])**2).sqrt()
        dot_product = Decimal(SO[0])*Decimal(SM[0]) + Decimal(SO[1])*Decimal(SM[1]) + Decimal(SO[2])*Decimal(SM[2])
        cos_val = Decimal(dot_product) / Decimal(b*c)
        # theta_lim = np.arccos( float(cos_val) )
        theta_lim = float(Decimal(2*(1-cos_val)).sqrt())

        return theta_lim

