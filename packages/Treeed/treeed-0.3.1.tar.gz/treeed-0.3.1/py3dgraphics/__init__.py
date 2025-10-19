# Выбор версии движка: 2 - Tkinter (старая), 3 - PyOpenGL (новая)
ENGINE_VERSION = 3

if ENGINE_VERSION == 2:
    from .graphics import Point3D, Object3D, Scene3D, create_cube, quick_scene, load_obj, create_object_from_file
elif ENGINE_VERSION == 3:
    from .opengl_graphics import Point3D, Object3D, Scene3D, create_cube, quick_scene, load_obj, create_object_from_file
else:
    raise ValueError("ENGINE_VERSION должен быть 2 или 3")

__version__ = "0.3.1"
__all__ = ["Point3D", "Object3D", "Scene3D", "create_cube", "quick_scene", "load_obj", "create_object_from_file", "ENGINE_VERSION"]
