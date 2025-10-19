
class RaySource:
    """
    Represents a source of rays in 3D space.

    Args:
        position_x (float): The x-coordinate of the ray source.
        position_y (float): The y-coordinate of the ray source.
        position_z (float): The z-coordinate of the ray source.
    """
    def __init__(self, position_x: float, position_y: float, position_z: float):
        self.x = position_x
        self.y = position_y
        self.z = position_z
        self.pt_origin = [self.x, self.y, self.z]

    def rays(self, theta, phi):
        """
        Abstract method to generate rays based on input angles.
        This method should be implemented by subclasses.

        Args:
            theta (float or np.ndarray): The polar angle(s) in radians.
            phi (float or np.ndarray): The azimuthal angle(s) in radians.

        Returns:
            tuple: A tuple containing:
                - u_dir (list or object): List of direction vectors (if theta or phi are arrays) or a single direction vector (if both are floats).
                - pt_o (list or object): List of origin points (if theta or phi are arrays) or a single origin point (if both are floats).
        """
        raise NotImplementedError("Subclasses must implement this method.")
    
