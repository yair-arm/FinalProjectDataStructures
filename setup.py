from setuptools import setup, find_packages

setup(
    name="cold-chain-optimization",
    version="2.0.0",
    description=(
        "Optimización de centros de refrigeración para pesca artesanal "
        "en Puerto Gaitán, Meta, Colombia — mediante teoría de grafos"
    ),
    author="Estructuras de Datos - Universidad",
    python_requires=">=3.10",
    packages=find_packages(),
    install_requires=[
        "matplotlib>=3.7",
        "numpy>=1.24",
        "folium>=0.14",
    ],
    extras_require={
        "geo": ["geopandas>=0.13", "shapely>=2.0", "pyproj>=3.5", "fiona>=1.9"],
        "dev": ["pytest>=7.4"],
    },
)
