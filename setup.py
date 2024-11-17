from setuptools import setup, find_packages

setup(
    name="tasepC",
    version="1.0.0",
    author="Theo Prada De Ville",
    author_email="DePradaVill@proton.me",
    scripts=["./tasepC/circuitGUI/gg.py"],
    install_requires=[
        "dearpygui==2.0.0",
        "numpy>=2.1.3"
    ],
    python_requires=">=3.8",
)