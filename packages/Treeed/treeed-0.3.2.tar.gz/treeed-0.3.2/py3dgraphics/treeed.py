"""
Treed - 3D Graphics Library
A comprehensive 3D graphics engine for Python with camera controls, object loading, and rendering.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'py3dgraphics'))

from py3dgraphics import (
    Point3D,
    Object3D,
    Scene3D,
    create_cube,
    quick_scene,
    load_obj
)

__version__ = "0.2.4"
__all__ = [
    "Point3D",
    "Object3D",
    "Scene3D",
    "create_cube",
    "quick_scene",
    "load_obj"
]
