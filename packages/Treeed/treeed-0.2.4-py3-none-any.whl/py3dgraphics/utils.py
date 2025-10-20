"""
Утилиты для Py3DGraphics: общие функции для обоих движков.
"""

import numpy as np

# Словарь для перевода названий цветов в формат RGB (0-255)
COLOR_MAP = {
    "white": (255, 255, 255), "black": (0, 0, 0),
    "red": (255, 0, 0), "green": (0, 255, 0),
    "blue": (0, 0, 255), "yellow": (255, 255, 0),
    "cyan": (0, 255, 255), "magenta": (255, 0, 255),
    "orange": (255, 165, 0), "purple": (128, 0, 128),
    "grey": (128, 128, 128), "gray": (128, 128, 128),
}

def normalize_color(color):
    """
    Принимает цвет в виде строки ("red"), кортежа (255,0,0) или (1.0,0,0)
    и всегда возвращает кортеж в формате (R, G, B) от 0.0 до 1.0.
    """
    if isinstance(color, str):
        # Если это строка, ищем ее в словаре
        rgb = COLOR_MAP.get(color.lower(), (255, 255, 255))  # По умолчанию белый
        return (rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0)

    elif isinstance(color, (list, tuple)) and len(color) == 3:
        # Если это кортеж/список, проверяем, в каком он формате
        is_normalized = all(0.0 <= c <= 1.0 for c in color)
        if is_normalized:
            return tuple(color)
        else:
            # Считаем, что это формат 0-255
            return (color[0] / 255.0, color[1] / 255.0, color[2] / 255.0)

    # Если формат не распознан, возвращаем белый цвет
    return (1.0, 1.0, 1.0)

def calculate_normal(p0, p1, p2):
    """
    Вычисляет нормаль к плоскости, заданной тремя точками.
    Возвращает нормализованный вектор нормали.
    """
    # Векторы из p0 в p1 и p0 в p2
    v1 = np.array(p1) - np.array(p0)
    v2 = np.array(p2) - np.array(p0)
    # Векторное произведение для нормали
    normal = np.cross(v1, v2)
    # Нормализация
    norm_length = np.linalg.norm(normal)
    if norm_length > 0:
        normal = normal / norm_length
    return normal

def generate_edges_from_faces(faces):
    """Создаёт уникальный список рёбер из списка граней."""
    edges = set()
    for face in faces:
        # Для каждой грани создаем рёбра между соседними вершинами
        for i in range(len(face)):
            p1_index = face[i]
            p2_index = face[(i + 1) % len(face)]  # Следующая вершина с переходом в начало

            # Добавляем ребро в set, чтобы избежать дубликатов.
            # Сортируем индексы, чтобы (0, 1) и (1, 0) считались одним и тем же ребром.
            edge = tuple(sorted((p1_index, p2_index)))
            edges.add(edge)

    return list(edges)

def load_obj(filename):
    """Загружает 3D модель из .obj файла и возвращает списки точек и граней."""
    points = []
    faces = []

    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split()
            if not parts:
                continue

            if parts[0] == 'v':
                # Вершина: v x y z
                if len(parts) >= 4:
                    x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                    points.append([x, y, z])
            elif parts[0] == 'f':
                # Грань: f v1 v2 v3 ...
                face_indices = []
                for part in parts[1:]:
                    # Разбираем индексы вершин (могут быть в формате v/vt/vn)
                    vertex_index = part.split('/')[0]
                    if vertex_index.isdigit():
                        face_indices.append(int(vertex_index) - 1)  # OBJ использует 1-based индексы
                if len(face_indices) >= 3:
                    faces.append(tuple(face_indices))

    return points, faces

def create_cube(size=150, speed=0.01, position=(0, 0, 0), color="white", fill=False, outline_color="white", line_width=2, speed_x=None, speed_y=None, speed_z=None):
    """Создаёт куб с заданными параметрами."""
    points = [
        [-size, -size, -size],
        [ size, -size, -size],
        [ size,  size, -size],
        [-size,  size, -size],
        [-size, -size,  size],
        [ size, -size,  size],
        [ size,  size,  size],
        [-size,  size,  size]
    ]
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),
        (4, 5), (5, 6), (6, 7), (7, 4),
        (0, 4), (1, 5), (2, 6), (3, 7)
    ]
    faces = [
        (0, 3, 2, 1),  # Задняя грань (-Z)
        (4, 5, 6, 7),  # Передняя грань (+Z)
        (1, 2, 6, 5),  # Верхняя грань (+Y)
        (0, 4, 7, 3),  # Нижняя грань (-Y)
        (4, 0, 1, 5),  # Левая грань (-X)
        (3, 7, 6, 2)   # Правая грань (+X)
    ]
    return points, edges, faces

def create_object_from_file(filename, **options):
    """Загружает модель из .obj и создает полностью готовый Object3D."""
    points, faces = load_obj(filename)
    if not points or not faces:
        return None  # Возвращаем None, если файл пуст или некорректен

    edges = generate_edges_from_faces(faces)

    # Импортируем Object3D здесь, чтобы избежать циклических импортов
    from .graphics import Object3D  # Для v2
    try:
        from .opengl_graphics import Object3D as OpenGLObject3D
        # Определяем, какой движок используется
        import os
        engine_choice = os.getenv('PY3D_ENGINE', '3')
        if engine_choice == '3':
            Object3D = OpenGLObject3D
    except ImportError:
        pass  # Если OpenGL не доступен, используем Tkinter

    # Создаем объект, передавая ему и грани, и сгенерированные рёбра
    return Object3D(points, edges=edges, faces=faces, **options)
