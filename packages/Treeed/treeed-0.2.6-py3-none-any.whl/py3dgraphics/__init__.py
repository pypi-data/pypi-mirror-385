# py3dgraphics/__init__.py
import os

# --- УМНЫЙ ПЕРЕКЛЮЧАТЕЛЬ ДВИЖКОВ ---

# Проверяем переменную окружения 'PY3D_ENGINE'.
# Если она не задана, по умолчанию будет использоваться '3' (PyOpenGL).
engine_choice = os.getenv('PY3D_ENGINE', '3')

if engine_choice == '2':
    # Если выбрана версия 2, импортируем все из старого движка Tkinter
    print("Py3DGraphics: Загружен движок Tkinter (v2)...")
    from .graphics import *
    from .editor import run_editor
    from .qt_editor import run_qt_editor

elif engine_choice == '3':
    # Если выбрана версия 3, импортируем все из нового движка PyOpenGL
    print("Py3DGraphics: Загружен движок PyOpenGL (v3)...")
    from .opengl_graphics import *
    from .editor import run_editor
    from .qt_editor import run_qt_editor
    from .physics_scene import PhysicsScene, create_physics_cube, quick_physics_scene

else:
    raise ImportError(
        f"Неверное значение для PY3D_ENGINE: '{engine_choice}'. Допустимы '2' или '3'."
    )


__version__ = "0.2.6"

# В __all__ перечисляем все функции и классы, которые должны быть доступны пользователю.
# Лучше перечислить все возможные имена из обоих движков.
__all__ = [
    # Общие классы и функции
    "Point3D", "Object3D", "Scene3D", "create_cube", "quick_scene",
    "load_obj", "generate_edges_from_faces", "create_object_from_file",

    # Специфичные для PyOpenGL (не страшно, если их нет в Tkinter-версии)
    "normalize_color", "COLOR_MAP",

    # Редактор сцен
    "run_editor", "run_qt_editor",

    # Физическая симуляция (только для PyOpenGL)
    "PhysicsScene", "create_physics_cube", "quick_physics_scene"
]
