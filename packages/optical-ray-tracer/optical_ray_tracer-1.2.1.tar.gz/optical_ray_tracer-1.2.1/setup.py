import os
from setuptools import setup, find_packages

def safe_read(filename, default=""):
    if not os.path.exists(filename):
        return default
    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
    for encoding in encodings:
        try:
            with open(filename, 'r', encoding=encoding) as f:
                content = f.read()
                if content.startswith('\ufeff'):
                    content = content[1:]
                return content
        except (UnicodeDecodeError, UnicodeError):
            continue
    return default

REQUIREMENTS = [
    "matplotlib>=3.4",
    "numpy>=1.21",
    "pandas>=1.3",
    "scipy>=1.7",
    "sympy>=1.9",
    "numba>=0.55"
]

long_description = safe_read("README.md", "Optical ray tracing package")

setup(
    name="optical-ray-tracer",
    version="1.2.1",
    author="Dam-Bè L. DOUTI, Henoc N'GASAMA, Serge DZO",
    author_email="ngasamah@gmail.com",
    description="Scientific package for optical ray tracing simulations.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Damzo/optical_ray_collector",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Physics"
    ],
    python_requires=">=3.8",
    install_requires=REQUIREMENTS,
    include_package_data=True,
    license="GPLv3",
    keywords="optics ray-tracing simulation physics"
)
