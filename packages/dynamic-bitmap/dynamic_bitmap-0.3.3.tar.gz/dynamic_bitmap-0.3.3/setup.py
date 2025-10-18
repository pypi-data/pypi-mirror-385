from setuptools import setup, find_packages

setup(
    name="dynamic-bitmap",
    version="0.3.3",
    author="Jesus Alberto Degollado Lopez",
    author_email="jesuslopez5587@gmail.com",
    description="Dynamic Parallel Bitmap con soporte de IA para búsquedas optimizadas, ahora con una vision sobre la conexion p2p.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/JesusDeg8061/Dynamic_bitmap",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.21",
        "tensorflow>=2.11",
        "scikit-learn>=1.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
)
