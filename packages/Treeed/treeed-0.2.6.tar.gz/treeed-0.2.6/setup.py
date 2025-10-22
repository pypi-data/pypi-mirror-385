from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="Treeed",
    version="0.2.6",
    author="Umar",
    author_email="umarfrost2011@gmail.com",
    description="Библиотека для создания и отображения 3D объектов с помощью PyOpenGL и Pygame",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.6",
    install_requires=[
        "numpy",
    ],
    extras_require={
        "opengl": [
            "pygame",
            "PyOpenGL",
            "PyOpenGL-accelerate",
        ],
        "physics": [
            "pybullet",
        ],
        "qt": [
            "PyQt5",
        ],
        "all": [
            "pygame",
            "PyOpenGL",
            "PyOpenGL-accelerate",
            "pybullet",
            "PyQt5",
        ],
    },
)
