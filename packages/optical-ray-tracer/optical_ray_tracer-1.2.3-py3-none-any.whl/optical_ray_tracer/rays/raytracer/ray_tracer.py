import numpy as np
import sympy as spy
from numba import njit
from typing import Union, List, Tuple


class Tracer:
    """
    Raytracer Class
    This class provides a symbolic ray tracing framework for simulating the interaction of rays with surfaces in 3D space. 
    It uses symbolic computation to calculate intersections, gradients, and reflections, enabling precise modeling of optical systems.
    Attributes:
        x, y, z, theta, phi (sympy.Symbol): Symbolic variables for 3D space and angles.
        i_vec, j_vec, k_vec (np.ndarray): Base vectors for the 3D coordinate system.
        incident_rays (dict): Dictionary to store incident rays with their direction vectors and origin points.
        surfaces (dict): Dictionary to store surfaces with their normal vectors, equations, and boundaries.
        reflected_rays (dict): Dictionary to store reflected rays with their direction vectors and origin points.
        lighting_scene (list): List of lighting scenes, each representing a ray tracing scenario.
    Methods:
        reset_scene():
            Resets the incident rays, surfaces, reflected rays, and lighting scenes.
        is_point_in_volume(point, p1, p2, p3, p4):
            Checks if a point is inside a volume defined by four points using barycentric coordinates.
        add_rays(vector_dir, point_origin, rays_dict=None):
            Adds a new ray to the specified dictionary of rays.
        add_surface(normal_vector, equation, boundaries, surfaces_dict=None):
            Adds a new surface to the specified dictionary of surfaces.
        symbolic_ray_equation(vector_dir, point_origin):
            Computes the parametric equations of a ray.
        symbolic_gradients(func):
            Computes the symbolic gradients of a given function.
        symbolic_incident_ray_intersection(inc_raysX, inc_raysY, surface):
            Computes the symbolic intersection equation between a ray and a surface.
        solve_incident_intersection(func, vector_dir, point_origin):
            Solves the intersection equation f(z)=0 and computes the intersection points.
        symbolic_surf_normal_unit_vec(func):
            Computes the symbolic unit normal vector of a surface.
        reflected_unit_vec(incident_vec, intersect_pt, surf_grad):
            Computes the unit vector of the reflected ray.
        trace_new_scene(incident_rays=None, surfaces=None, reflected_rays=None):
            Traces rays in the scene, computes intersections, and calculates reflected rays.
    """

    def __init__(self):
        self.x, self.y, self.z, self.theta, self.phi = spy.symbols('x y z theta phi')
        
        # Base vectors
        # self.i_vec = np.array([1, 0, 0])
        # self.j_vec = np.array([0, 1, 0])
        # self.k_vec = np.array([0, 0, 1])
        
        # Incident rays
        self.incident_rays = {}

        # Surfaces
        self.surfaces = {}
        
        # Reflected rays
        self.reflected_rays = {}
        
        # Liste of lighting scenes
        self.lighting_scene = []

    def reset_scene(self) -> None:
        """
        Resets the incident rays, surfaces, reflected rays, and lighting scenes.
        """
        self.incident_rays = {}
        self.surfaces = {}
        self.reflected_rays = {}
        self.lighting_scene = []
        return None


    def add_rays(self, vector_dir: Union[np.ndarray, list], point_origin: Union[np.ndarray, list], rays_dict: dict = None)-> Tuple[int, dict]: # type: ignore
        """
        Adds a new entry to the dictionary of optical rays
        
        Args:
            vector_dir (list or np.array): Coordinates [x, y, z] of the direction vector
            point_origin (list or np.array): Coordinates [x, y, z] of the origin point
            rays_dict (dict, optional): Existing dictionary of rays. If None, the default global incident rays dictionary is used.
        
        Returns:
            tuple: (int, dict) - Index of the new entry and the updated dictionary
        """
        # TODO : implémenter la possibilité d'ajouter une liste de rays ???
        use_global_dict = False
        if rays_dict is None:
            rays_dict = self.incident_rays
            use_global_dict = True
        
        vector_dir = np.array(vector_dir) if not isinstance(vector_dir, np.ndarray) else vector_dir
        point_origin = np.array(point_origin) if not isinstance(point_origin, np.ndarray) else point_origin
        
        if vector_dir.shape != (3,) or point_origin.shape != (3,):
            raise ValueError("Vectors should have their three coordinates (x, y, z)")
        
        new_index = max(rays_dict.keys()) + 1 if rays_dict else 0
        rays_dict[new_index] = [vector_dir, point_origin]

        if use_global_dict:
            self.incident_rays.update(rays_dict)
        
        return new_index, rays_dict

    def add_surface(self, equation: Union[str, List[str]], boundaries: Union[List[List[float]], List[List[float]]], surfaces_dict: dict = None)-> Tuple[int, dict]: # type: ignore
        """
        Adds a new entry to the dictionary of surfaces
        
        Args:
            normal_vector (Union[np.ndarray, list]): Coordinates [x, y, z] of the normal vector
            equation (str): Surface equation as a string (e.g., "x**2 + y**2 - z")
            boundaries (Union[list[list[float]], list[list[float]]]): List of boundaries [[xmin, xmax], [ymin, ymax], [zmin, zmax]]
            surfaces_dict (dict, optional): Existing dictionary of surfaces. If None, the default dictionary is used.
        
        Returns:
            tuple: (int, dict) - Index of the new entry and the updated dictionary
        """
        use_global_dict = False
        if surfaces_dict is None:
            surfaces_dict = self.surfaces
            use_global_dict = True
        
        # # Convert the normal vector to numpy array
        # normal_vector = np.array(normal_vector) if not isinstance(normal_vector, np.ndarray) else normal_vector
        
        # # Check dimensions
        # if normal_vector.shape != (3,):
        #     raise ValueError("The normal vector must be of dimension 3 (x, y, z)")

        # Check equation format
        if isinstance(equation, list) and len(boundaries) != len(equation):
            raise ValueError("If multiple equations are provided, the number of boundaries must match the number of equations")
        elif isinstance(equation, str):
            if len(boundaries) != 3 or not all(len(bound) == 2 for bound in boundaries):
                raise ValueError("Boundaries must be in the format [[xmin, xmax], [ymin, ymax], [zmin, zmax]]")
            equation = [equation]
            boundaries = [boundaries]  # Wrap in a list for consistency
        
        # Convert the equation string to a sympy expression
        func = []
        try:
            for equ in equation:
                # Create the sympy expression from the string
                expr = spy.sympify(equ)
                # Check that the expression only uses x, y, z as variables
                if not all(str(sym) in ['x', 'y', 'z'] for sym in expr.free_symbols):
                    raise ValueError("The equation expression should contain only x, y, z as variables")
                # Create the sympy function with the class symbols
                func.append(expr.subs({'x': self.x, 'y': self.y, 'z': self.z}))
        except spy.SympifyError as exc:
            raise ValueError("The given equation is not a valid mathematical expression") from exc
        
        new_index = -1
        for f, bounds in zip(func, boundaries):
            # Ajout au dictionnaire
            new_index = max(surfaces_dict.keys()) + 1 if surfaces_dict else 0
            # surfaces_dict[new_index] = [normal_vector, func, boundaries]
            surfaces_dict[new_index] = [f, bounds]

        if use_global_dict:
            self.surfaces.update(surfaces_dict)
        
        return new_index, surfaces_dict

    # @njit
    def trace_new_scene(self, incident_rays: Union[list, dict] = {}, surfaces: dict = {}, reflected_rays: dict = {}, parallel_lighting: bool = False)-> Tuple[dict, dict]: 
        """
        Traces rays through a scene, computing the closest intersection points and corresponding reflected rays for each incident ray with all provided surfaces.
        This method supports both sequential and parallel lighting scenarios. For parallel lighting, the number of incident rays must match the number of surfaces.
            incident_rays (Union[List[dict], dict], optional): Dictionary or list of dictionaries containing incident rays. 
                If None, uses self.incident_rays.
            surfaces (dict, optional): Dictionary of surfaces, where each surface is defined by its normal vector, 
                surface function, and boundaries. If None, uses self.surfaces.
            reflected_rays (dict, optional): Dictionary to store reflected rays. If None, uses self.reflected_rays.
            parallel_lighting (bool, optional): If True, assumes parallel lighting where each surface receives its own set of incident rays. 
                Defaults to False.
        Raises:
            ValueError: If parallel_lighting is True and the number of incident rays does not match the number of surfaces.
            tuple: 
                - intersection_points (dict): Dictionary mapping ray indices to their closest intersection points with the surfaces.
                - reflected_rays (dict): Dictionary containing the reflected rays generated at each intersection.
        """
        
        """
        Ray tracing algorithm to compute the closest intersection points
        and the reflected rays for each incident ray with all surfaces.

        Args:
            incident_rays (dict, optional): Dictionary of incident rays. If None, uses self.incident_rays.
            surfaces (dict, optional): Dictionary of surfaces. If None, uses self.surfaces.
            reflected_rays (dict, optional): Dictionary of reflected rays. If None, uses self.reflected_rays.

        Returns:
            tuple: (dict, dict) - (Closest intersection points, Corresponding reflected rays)
        """
        # Initialize dictionaries
        if not incident_rays:
            incident_rays = self.incident_rays
        if not surfaces:
            surfaces = self.surfaces
        if not reflected_rays:
            reflected_rays = self.reflected_rays

        # Initialize nearest_point with very large numbers
        nearest_point = [float('inf')] * len(incident_rays)
        # Dictionary to store the closest intersection points
        intersection_points = {}

        # Dictionary to store reflected rays per surface
        surface_reflected_rays = {}

        # If parallel lighting activated, incident_rays dict should be list(dict)
        if (parallel_lighting and len(incident_rays) != len(surfaces)) or (isinstance(incident_rays, list) and len(incident_rays) != len(surfaces)):
            raise ValueError("For parallel lighting or with a list of incident rays, " \
            "the number of incident rays dictionnaries in the list must match the number of surfaces.")
        
        # Loop over surfaces
        for surf_idx, surface in surfaces.items():
            
            surf_func, boundaries = surface
            # Initialize the dictionary of reflected rays for this surface
            surface_reflected_rays[surf_idx] = {}

            # Compute the symbolic expression of the unit normal vector
            surf_normal_symbolic = self.__symbolic_surf_normal_unit_vec(surf_func)

            # if parallel lighting activated, then choose the corresponding incident rays
            incident_rays_dict = {}
            if parallel_lighting or isinstance(incident_rays, list):
                incident_rays_dict = incident_rays[surf_idx]
            else: # If on the first surface of the scene, use incident rays dict, else use reflected rays from the previous surface
                if surf_idx == 0: incident_rays_dict = incident_rays 
                else: incident_rays_dict = surface_reflected_rays[surf_idx-1]

            # Loop over incident rays
            for ray_idx, ray in incident_rays_dict.items(): # type: ignore
                vector_dir, point_origin = ray

                # Compute the parametric equations of the ray
                x_equ, y_equ = self.__symbolic_ray_equation(vector_dir, point_origin)

                # Compute the intersection equation
                intersection_equ = self.__symbolic_incident_ray_intersection(x_equ, y_equ, surf_func)

                # Compute the intersection points
                intersect_list = self.__solve_incident_intersection(intersection_equ, vector_dir, point_origin)

                if not intersect_list:  # If no intersection, move to the next ray
                    continue

                # Filter intersection points that are inside the volume
                valid_points = []
                for point in intersect_list:
                    if self.__is_point_in_volume(point, boundaries):
                        valid_points.append(point)

                if not valid_points:  # If no valid points, move to the next ray
                    continue

                # Compute distances between the ray origin point and the intersection points
                distances = []
                for i, point in enumerate(valid_points):
                    dist = np.linalg.norm(point - point_origin)
                    distances.append((dist, i))

                # Find the closest intersection point and update the nearest_point and intersection_points dictionaries
                for dist, idx in distances:
                    if dist < nearest_point[ray_idx]:
                        nearest_point[ray_idx] = dist
                        intersection_points[ray_idx] = valid_points[idx]

                # Compute the reflected unit vector
                reflected_dir = self.__reflected_unit_vec(vector_dir, intersection_points[ray_idx], surf_normal_symbolic)

                # Add the reflected ray to the global dictionary
                refl_idx, self.reflected_rays = self.add_rays(reflected_dir, intersection_points[ray_idx], reflected_rays)

                # Store the reflected ray for this surface
                surface_reflected_rays[surf_idx][ray_idx] = refl_idx

            # Create the lighting scene
            scene = {surf_idx: [incident_rays_dict, {k: reflected_rays[v] for k, v in surf_refl.items()}]
                    for surf_idx, surf_refl in surface_reflected_rays.items() if surf_refl}

            # Add the scene to the list of scenes
            if scene:
                self.lighting_scene.append(scene)

        return intersection_points, reflected_rays

    def __symbolic_ray_equation(self, vector_dir: np.ndarray, point_origin: np.ndarray)-> Tuple[spy.Function, spy.Function]:
        """
        Computes the parametric equations of the ray, given its direction vector and origin point.
        
        Args:
            vector_dir (np.ndarray): Direction vector of the ray
            point_origin (np.ndarray): Origin point of the ray
            
        Returns:
            tuple: (x_equ, y_equ) parametric equations of the ray: x=f(z) and y=f(z)
        """
        x_equ = (self.z - point_origin[2]) / vector_dir[2] * vector_dir[0] + point_origin[0]
        y_equ = (self.z - point_origin[2]) / vector_dir[2] * vector_dir[1] + point_origin[1]
        
        return x_equ, y_equ

    def __symbolic_gradients(self, func: spy.Function)-> Tuple[spy.Derivative, spy.Derivative, spy.Derivative]:
        """
        Computes the symbolic gradients of a given function
        """
        df_x = spy.diff(func, self.x)
        df_y = spy.diff(func, self.y)
        df_z = spy.diff(func, self.z)
        
        return df_x, df_y, df_z

    def __symbolic_incident_ray_intersection(self, inc_raysX: spy.Function, inc_raysY: spy.Function, surface: spy.Function)-> spy.Function:
        """
        Computes the symbolic intersection equation between a ray and a surface
        """
        intersection = surface.subs({self.x: inc_raysX, self.y: inc_raysY})
        
        return spy.simplify(intersection)

    def __solve_incident_intersection(self, func: spy.Function, vector_dir: np.ndarray, point_origin: np.ndarray):
        """
        Solves the intersection equation f(z)=0 and computes the intersection points
        
        Args:
            func (spy.Function): Equation of the form f(z)=0
            vector_dir (np.ndarray): Direction vector of the ray
            point_origin (np.ndarray): Origin point of the ray
            
        Returns:
            list: List of the intersection points [x, y, z]
        """
        # Solve the equation f(z)=0
        z_solutions = spy.solve(func, self.z)
        
        # Get the parametric equation of the ray
        x_equ, y_equ = self.__symbolic_ray_equation(vector_dir, point_origin)
        
        # Compute the intersection points for each z solution
        intersection_points = []
        for z_sol in z_solutions:
            # convert the symbolic solution to a float
            z_val = float(z_sol)
            # Compute the corresponding x and y coordinates
            x_val = float(x_equ.subs(self.z, z_val)) # type: ignore
            y_val = float(y_equ.subs(self.z, z_val)) # type: ignore
            # Create the intersection point
            p = np.array([x_val, y_val, z_val])
            intersection_points.append(p)
            
        return intersection_points

    def __symbolic_surf_normal_unit_vec(self, func: spy.Function)-> List[spy.Function]:
        """
        Computes the unit normal vector to the surface symbolically
        
        Args:
            func (spy.Function): Sympy expression of the surface
            
        Returns:
            list: List of normalized components [x_norm, y_norm, z_norm] of the normal vector (sympy expressions)
        """
        # Compute the gradients
        grad_x, grad_y, grad_z = self.__symbolic_gradients(func)
        
        # Compute the norm of the gradient vector
        norm = spy.sqrt(grad_x**2 + grad_y**2 + grad_z**2) # type: ignore
        
        # Normalize the components
        x_norm = grad_x / norm # type: ignore
        y_norm = grad_y / norm # type: ignore
        z_norm = grad_z / norm # type: ignore
        
        return [x_norm, y_norm, z_norm]

    def __reflected_unit_vec(self, incident_vec: np.ndarray, intersect_pt: np.ndarray, surf_grad: list)-> np.ndarray:
        """
        Computes the reflected unit vector
        
        Args:
            incident_vec (np.ndarray): Incident vector
            intersect_pt (np.ndarray): Intersection point [x, y, z]
            surf_grad (list): List of symbolic components of the normal vector [x_norm, y_norm, z_norm]
            
        Returns:
            np.ndarray: Reflected unit vector coordinates [x, y, z]
        """
        # Evaluate the symbolic expressions at the intersection point
        x_val = float(surf_grad[0].subs({self.x: intersect_pt[0], 
                                        self.y: intersect_pt[1], 
                                        self.z: intersect_pt[2]}))
        y_val = float(surf_grad[1].subs({self.x: intersect_pt[0], 
                                        self.y: intersect_pt[1], 
                                        self.z: intersect_pt[2]}))
        z_val = float(surf_grad[2].subs({self.x: intersect_pt[0], 
                                        self.y: intersect_pt[1], 
                                        self.z: intersect_pt[2]}))
        
        # Numerical value of the normal vector at the intersection point
        normal_vec = np.array([x_val, y_val, z_val])
        
        # Calcul du vecteur réfléchi
        return incident_vec - 2 * np.dot(incident_vec, normal_vec) * normal_vec

    @staticmethod
    def __is_point_in_volume(test_point: np.ndarray, bounds: List[List[float]]) -> bool:

        """
        Check if a point M(x, y, z) is inside the volume defined by four points using barycentric coordinates.
        This method determines whether a given point lies within a tetrahedron formed by four points in 3D space.

        Args:
            test_point (np.ndarray): Coordinates [x, y, z] of the point to test.
            bounds (list[list[float]]): List of boundaries [[xmin, xmax], [ymin, ymax], [zmin, zmax]]

        Returns:
            bool: True if the point is inside the volume, False otherwise.
        """

        return (
                (bounds[0][0] <= test_point[0] <= bounds[0][1]) and
                (bounds[1][0] <= test_point[1] <= bounds[1][1]) and
                (bounds[2][0] <= test_point[2] <= bounds[2][1])
        )

if __name__ == "__main__":

    
    from configurations.geometries import parabolic 
    from rays.source import point_source
    from rays.raytracer import ray_tracer
    import pathlib
    import sys
    # Ajouter le dossier racine du projet au sys.path
    project_root = pathlib.Path(__file__).parent.parent.resolve()
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    # Création d'une instance de la classe
    print("Initialisation du ray tracer...")
    ray_tracer = ray_tracer.Tracer()

    # Test: Ajout de surfaces
    print("\nAjout de surfaces")
    # Surface parabolique
    parab_1 = parabolic.ParabolicReflector()
    print(parab_1.boundaries())
    surface1_idx, _ = ray_tracer.add_surface(
        str(parab_1.symbolic_equation()),  # Équation du paraboloïde
        parab_1.boundaries()  # Limites du volume
    )
    print(f"Surface 1 ajoutée (idx={surface1_idx}): paraboloïde {str(parab_1.symbolic_equation())}")

    # Test : Ajout de rayons incidents
    ptSrce = point_source.Source()
    print("\nTest: Ajout de rayons incidents venant de la source")
    # Rayons venant du point source et couvrant tout le reflecteur
    vec_dir, pt_orig = parab_1.generate_rays_from_source(64, ptSrce)
    for i in range(len(vec_dir)):
        ray_idx, _ = ray_tracer.add_rays(vec_dir[i], pt_orig[i])
        print(f"Rayon ajouté (idx={ray_idx}): direction={vec_dir[i]}, origine={pt_orig[i]}")
    
    
    # Test: Calcul des intersections et des réflexions
    print("\nTest: Calcul des intersections et des réflexions")
    intersections, reflected = ray_tracer.trace_new_scene()
    
    # Affichage des résultats
    print("\nRésultats:")
    print("Points d'intersection trouvés:")
    for ray_idx, point in intersections.items():
        print(f"Rayon {ray_idx}: point d'intersection = {point}")
    
    print("\nRayons réfléchis générés:")
    for ray_idx, (dir_vec, origin) in reflected.items():
        print(f"Rayon réfléchi {ray_idx}: direction={dir_vec}, origine={origin}")
    
    print("\nScènes d'éclairage enregistrées:")
    for i, scene in enumerate(ray_tracer.lighting_scene):
        print(f"\nScène {i}:")
        for surf_idx, (inc_rays, refl_rays) in scene.items():
            print(f"Surface {surf_idx}:")
            print(f"  Nombre de rayons incidents: {len(inc_rays)}")
            print(f"  Nombre de rayons réfléchis: {len(refl_rays)}") 
