import sys
import pathlib
import os
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Ajouter le dossier racine du projet au sys.path
project_root = pathlib.Path(__file__).parent.parent.resolve()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
# working_dir = str(pathlib.Path().resolve())

# Imports des modules du projet
from optical_ray_tracer.configurations.geometries.Parabolic import ParabolicReflector
from optical_ray_tracer.configurations.geometries.Cylindric import CylindricalReflector
from optical_ray_tracer.configurations.geometries.ring_array import RingarrayReflector
from optical_ray_tracer.configurations.geometries.given_geometry import GivenGeometry
from optical_ray_tracer.rays.source.point_source import Source as PointSource
from optical_ray_tracer.rays.source.large_source import Source as LargeSource
from optical_ray_tracer.rays.raytracer.ray_tracer import Tracer
from optical_ray_tracer.utils.rotation_vect import rotationVectU
from optical_ray_tracer.utils.sphericalcartesian import sphericalcartesian as spherical_to_cartesian


# --- Adaptation des sources pour générer l'attribut pt_origin ---
class PointSourceAdapted(PointSource):
    def __init__(self, origin):
        super().__init__()
        self.pt_origin = np.array(origin)
    def rays(self, theta, phi):
        return super().rays(theta, phi)


class LargeSourceAdapted(LargeSource):
    def __init__(self, x, y, z, source_extent):
        super().__init__(x, y, z, source_extent)
        self.pt_origin = np.array([x, y, z])
    def rays(self, theta, phi):
        return super().rays(theta, phi)


def test_geometry(geom, source_class, source_origin=[0,0,0], n_rays=9, bounds=None):
    print(f"\n--- Testing {geom.__class__.__name__} ---")
    tracer = Tracer()

    # Ajouter surface
    surface_idx, _ = tracer.add_surface(
        equation=str(geom.symbolic_equation()),
        boundaries=bounds if bounds else geom.boundaries()
    )
    print(f"Surface ajoutée: idx={surface_idx}, équation={geom.symbolic_equation()}")
    print("Boundaries:", bounds if bounds else geom.boundaries())
    print("Collection area:", geom.collection_area())

    # Initialiser source
    pt_source = source_class(source_origin)

    # Générer rayons
    vec_dir, pt_orig = geom.generate_rays_from_source(n_rays, pt_source)
    for i in range(len(vec_dir)):
        idx, _ = tracer.add_rays(vec_dir[i], pt_orig[i])
        print(f"Rayon ajouté idx={idx}, direction={vec_dir[i]}, origine={pt_orig[i]}")

    # Calcul intersections et réflexions
    intersections, reflected = tracer.trace_new_scene()
    print("\nPoints d'intersection trouvés:")
    for ray_idx, point in intersections.items():
        print(f"Rayon {ray_idx}: point d'intersection = {point}")
    print("\nRayons réfléchis générés:")
    for ray_idx, (dir_vec, origin) in reflected.items():
        print(f"Rayon réfléchi {ray_idx}: direction={dir_vec}, origine={origin}")

    # Affichage détaillé des scènes d'éclairage
    print("\nScènes d'éclairage enregistrées:")
    for i, scene in enumerate(tracer.lighting_scene):
        print(f"\nScène {i}:")
        for surf_idx, (inc_rays, refl_rays) in scene.items():
            print(f"Surface {surf_idx}:")
            print(f"  Nombre de rayons incidents: {len(inc_rays)}")
            print(f"  Nombre de rayons réfléchis: {len(refl_rays)}") 

    return pt_orig, vec_dir, intersections, reflected, geom


def animate_rays_interactive(pt_orig, vec_dir, intersections, geom):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.set_box_aspect([1,1,1])

    # Rayons incidents
    for i in range(len(pt_orig)):
        ray = np.array([pt_orig[i], pt_orig[i]+np.array(vec_dir[i])*1.0])
        ax.plot(ray[:,0], ray[:,1], ray[:,2], color='blue', alpha=0.7)

    # Points d'intersection
    if intersections and len(intersections) > 0:
        inters = np.array([pt if isinstance(pt, (list, np.ndarray)) else list(pt.values()) for pt in intersections.values()])
        ax.scatter(inters[:,0], inters[:,1], inters[:,2], color='red', s=20, label='Intersections') # type: ignore

    # Surface (approximation par points)
    try:
        bounds = geom.boundaries()
        X = np.linspace(bounds[0][0], bounds[0][1], 20)
        Y = np.linspace(bounds[1][0], bounds[1][1], 20)
        X, Y = np.meshgrid(X, Y)
        if hasattr(geom, "equation_function"):
            Z = np.array([geom.equation_function(x, y) for x, y in zip(X.flatten(), Y.flatten())]).reshape(X.shape)
            ax.plot_surface(X, Y, Z, color='orange', alpha=0.3)
    except Exception as e:
        print("Surface plotting skipped:", e)

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    plt.title(f"Visualization: {geom.__class__.__name__}")
    plt.legend()
    plt.show()


def test_geometries():
    # Parabolic
    parab = ParabolicReflector(f_x=1.0, f_y=1.0, h=2.0, rotation_angle=0.0)
    pt_orig, vec_dir, intersections, _, geom = test_geometry(parab, PointSourceAdapted, [0,0,0], n_rays=9)
    animate_rays_interactive(pt_orig, vec_dir, intersections, geom)

    # Cylindrical
    cyl = CylindricalReflector(length=2.0, height=1.0, thickness=0.5, rot_angle=0.0)
    pt_orig, vec_dir, intersections, _, geom = test_geometry(cyl, PointSourceAdapted, [0,0,0], n_rays=9)
    animate_rays_interactive(pt_orig, vec_dir, intersections, geom)

    # RingArray
    ring = RingarrayReflector(rotation_angle=0.0, Rin_0=0.5, N_rings=3, A_target=2.0, material_w=0.1, h_max=1.0)
    pt_orig, vec_dir, intersections, _, geom = test_geometry(ring, PointSourceAdapted, [0,0,0], n_rays=9)
    animate_rays_interactive(pt_orig, vec_dir, intersections, geom)

    # GivenGeometry
    eq_str = "z - x**2 - y**2"
    given_geom = GivenGeometry(rotation_angle=0.0, equation=eq_str)
    bounds = given_geom.boundaries(-1,1,-1,1,0,2)
    pt_orig, vec_dir, intersections, _, geom = test_geometry(given_geom, PointSourceAdapted, [0,0,-1], n_rays=4, bounds=bounds)
    animate_rays_interactive(pt_orig, vec_dir, intersections, geom)


def test_sources():
    print("\n--- Testing PointSource ---")
    source_pt = PointSourceAdapted([0,0,1.5e8])
    rays_pt = source_pt.rays(0.0, 0.0)
    print("Point source rays directions:", rays_pt[0])
    print("Point source rays origins:", rays_pt[1])

    print("\n--- Testing LargeSource ---")
    source_large = LargeSourceAdapted(0,0,0,1.0)
    theta_phi = np.linspace(0,0.5,5)
    vec_dir, pt_orig = source_large.rays(theta_phi, theta_phi)
    print("Large source rays directions:", vec_dir)
    print("Large source rays origins:", pt_orig)


def test_utils():
    print("\n--- Testing utils ---")
    cart = spherical_to_cartesian([0.5,1.0])
    print("Spherical -> Cartesian:", cart)
    rot = rotationVectU([1,0,0],1.57)
    print("Rotation matrix:", rot)


if __name__ == "__main__":
    test_geometries()
    test_sources()
    test_utils()
