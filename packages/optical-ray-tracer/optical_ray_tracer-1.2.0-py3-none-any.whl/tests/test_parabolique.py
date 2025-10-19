"""
test_parabolic.py

Unit test for the ParabolicReflector class and the Tracer in the OPTICAL_RAY_COLLECTOR project.

This script checks:
1. Initialization of the Tracer.
2. Addition of a parabolic surface.
3. Generation of incident rays from a point light source.
4. Computation of intersections and reflected rays.
5. Recording of lighting scenes.

No visualization is included; this test is purely textual and serves to validate the core logic.
"""

if __name__ == "__main__":

    # Import required modules
    import pathlib
    import sys

    # Add the project root directory to sys.path for relative imports
    project_root = pathlib.Path(__file__).parent.parent.resolve()
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    from configurations.geometries import Parabolic   # ParabolicReflector class
    from rays.source import point_source              # Point light source
    from rays.raytracer import ray_tracer             # Main tracer engine

    # -----------------------------------------------
    # 1. Tracer Initialization
    # -----------------------------------------------
    print("Initializing the ray tracer...")
    tracer = ray_tracer.Tracer()
    
    # -----------------------------------------------
    # 2. Create and add a parabolic surface
    # -----------------------------------------------
    print("\nAdding optical surfaces...")

    parab = Parabolic.ParabolicReflector()
    boundaries = parab.boundaries()
    print(f"Parabolic surface boundaries: {boundaries}")

    # Add the surface to the tracer
    surface_idx, _ = tracer.add_surface(
        str(parab.symbolic_equation()),  # Symbolic equation
        boundaries                       # Volume boundaries
    )
    print(f"Surface {surface_idx} added: {str(parab.symbolic_equation())}")

    # -----------------------------------------------
    # 3. Generate incident rays from the source
    # -----------------------------------------------
    print("\nGenerating incident rays from the source...")
    source = point_source.Source()
    n_rays = 5  # Number of rays to generate
    vec_dir, pt_orig = parab.generate_rays_from_source(n_rays, source)

    for i in range(len(vec_dir)):
        ray_idx, _ = tracer.add_rays(vec_dir[i], pt_orig[i])
        print(f"Ray added (idx={ray_idx}): direction={vec_dir[i]}, origin={pt_orig[i]}")

    # -----------------------------------------------
    # 4. Compute intersections and reflections
    # -----------------------------------------------
    print("\nComputing intersections and reflections...")
    intersections, reflected = tracer.trace_new_scene()

    # -----------------------------------------------
    # 5. Display results
    # -----------------------------------------------
    print("\nResults:")
    
    print("Intersection points found:")
    for ray_idx, point in intersections.items():
        print(f"Ray {ray_idx}: intersection point = {point}")
    
    print("\nGenerated reflected rays:")
    for ray_idx, (dir_vec, origin) in reflected.items():
        print(f"Reflected ray {ray_idx}: direction={dir_vec}, origin={origin}")
    
    print("\nRecorded lighting scenes:")
    for i, scene in enumerate(tracer.lighting_scene):
        print(f"\nScene {i}:")
        for surf_idx, (inc_rays, refl_rays) in scene.items():
            print(f"Surface {surf_idx}:")
            print(f"  Number of incident rays: {len(inc_rays)}")
            print(f"  Number of reflected rays: {len(refl_rays)}")
