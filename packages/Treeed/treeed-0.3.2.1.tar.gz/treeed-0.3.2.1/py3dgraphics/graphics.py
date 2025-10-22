import tkinter as tk
import math
import numpy as np
from .utils import normalize_color, generate_edges_from_faces, load_obj, create_cube as create_cube_data, create_object_from_file as create_object_from_file_base

class Point3D:
    """Класс для представления 3D точки."""
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def to_list(self):
        return [self.x, self.y, self.z]

class Object3D:
    """Класс для 3D объекта с точками, рёбрами и гранями."""
    def __init__(self, points, edges=None, faces=None, speed=0.01, position=(0, 0, 0), color="white", fill=False, outline_color="white", line_width=2, speed_x=None, speed_y=None, speed_z=None):
        # Храним оригинальные точки как numpy array
        self.base_points = np.array(points, dtype=float)
        # А эти точки будем изменять и отрисовывать
        self.points = np.array(points, dtype=float)
        self.edges = edges  # Для каркасного режима
        self.faces = faces  # Для полигонального режима
        self.position = np.array(position, dtype=float)
        self.angle_x = 0
        self.angle_y = 0
        self.angle_z = 0
        self.speed = speed  # Общая скорость вращения
        self.speed_x = speed_x if speed_x is not None else speed  # Скорость вращения по X
        self.speed_y = speed_y if speed_y is not None else speed  # Скорость вращения по Y
        self.speed_z = speed_z if speed_z is not None else speed  # Скорость вращения по Z
        self.color = normalize_color(color)  # Нормализуем цвет
        self.fill = fill  # Флаг заливки граней
        self.outline_color = normalize_color(outline_color)  # Нормализуем цвет контура
        self.line_width = line_width  # Толщина линий рёбер

    def set_position(self, x, y, z):
        """Устанавливает новую позицию объекта."""
        self.position[0] = x
        self.position[1] = y
        self.position[2] = z

    def move(self, dx, dy, dz):
        """Перемещает объект относительно текущей позиции."""
        self.position[0] += dx
        self.position[1] += dy
        self.position[2] += dz

    def rotate_points(self, points, angle_x, angle_y, angle_z):
        """Векторное вращение всех точек объекта."""
        # Матрицы вращения
        Rx = np.array([
            [1, 0, 0],
            [0, math.cos(angle_x), -math.sin(angle_x)],
            [0, math.sin(angle_x), math.cos(angle_x)]
        ])
        Ry = np.array([
            [math.cos(angle_y), 0, math.sin(angle_y)],
            [0, 1, 0],
            [-math.sin(angle_y), 0, math.cos(angle_y)]
        ])
        Rz = np.array([
            [math.cos(angle_z), -math.sin(angle_z), 0],
            [math.sin(angle_z), math.cos(angle_z), 0],
            [0, 0, 1]
        ])
        # Общая матрица вращения
        R = Rz @ Ry @ Rx
        # Применяем вращение
        return points @ R.T

    def project(self, scale, width, height):
        """Проецирует точки объекта в 2D."""
        # Векторная проекция
        points_with_pos = self.points + self.position
        z = points_with_pos[:, 2]
        factor = scale / (z + 500)
        x_2d = points_with_pos[:, 0] * factor + width / 2
        y_2d = points_with_pos[:, 1] * factor + height / 2
        return list(zip(x_2d, y_2d))

    def update_rotation(self):
        """Обновляет углы и поворачивает объект, исходя из ОРИГИНАЛЬНЫХ точек."""
        if self.speed > 0 or self.speed_x > 0 or self.speed_y > 0 or self.speed_z > 0:
            self.angle_x += self.speed_x
            self.angle_y += self.speed_y
            self.angle_z += self.speed_z

            # Векторное вращение всех точек
            self.points = self.rotate_points(self.base_points, self.angle_x, self.angle_y, self.angle_z)

class Scene3D:
    """Класс для управления 3D сценой."""
    def __init__(self, width=600, height=600, title="3D Сцена", bg="black", master=None):
        self.width = width
        self.height = height
        self.scale = 200
        self.objects = []
        if master:
            self.window = master  # Use provided master window (e.g., Toplevel)
        else:
            self.window = tk.Tk()  # Create new root window
        self.window.title(title)
        self.canvas = tk.Canvas(self.window, width=width, height=height, bg=bg)
        self.canvas.pack()
        self.player = None  # Управляемый объект
        self.move_speed = 10  # Скорость движения
        self.window.bind("<KeyPress>", self.on_key_press)

    def add_object(self, obj):
        """Добавляет объект в сцену."""
        self.objects.append(obj)

    def update(self):
        """Главный цикл анимации. Обновляет логику, перерисовывает сцену и планирует следующий кадр."""
        self.canvas.delete("all")
        # Список всех полигонов для Z-сортировки
        polygons = []
        wireframe_objects = []  # Список каркасных объектов для отрисовки после полигонов
        for obj in self.objects:
            obj.update_rotation()
            projected_points = obj.project(self.scale, self.width, self.height)
            if obj.faces:
                # Рисуем полигоны
                for face in obj.faces:
                    # Вычисляем среднюю Z для сортировки
                    if max(face) < len(obj.points):
                        z_avg = np.mean(obj.points[face, 2] + obj.position[2])
                        points_2d = [projected_points[i] for i in face]
                    else:
                        continue  # Skip invalid faces
                    # Сохраняем все нужные свойства для отрисовки
                    render_properties = {
                        "is_filled": obj.fill,
                        "fill_color": self._color_to_hex(obj.color),
                        "outline_color": self._color_to_hex(obj.outline_color),
                        "line_width": obj.line_width
                    }
                    polygons.append((z_avg, points_2d, render_properties))
            elif obj.edges:
                # Сохраняем каркасные объекты для отрисовки после полигонов
                wireframe_objects.append((obj, projected_points))
        # Сортировка полигонов по Z (от дальних к ближним)
        polygons.sort(key=lambda x: x[0], reverse=True)
        for _, points_2d, props in polygons:
            fill_color = props["fill_color"] if props["is_filled"] else ""
            self.canvas.create_polygon(points_2d, outline=props["outline_color"], fill=fill_color, width=props["line_width"])
        # Отрисовка каркасных объектов после полигонов
        for obj, projected_points in wireframe_objects:
            for edge in obj.edges:
                p1 = projected_points[edge[0]]
                p2 = projected_points[edge[1]]
                self.canvas.create_line(p1[0], p1[1], p2[0], p2[1], fill=self._color_to_hex(obj.outline_color), width=obj.line_width)
        self.window.after(16, self.update)  # ~60 FPS

    def _color_to_hex(self, color):
        """Конвертирует нормализованный цвет (0-1) в hex для Tkinter."""
        r, g, b = int(color[0] * 255), int(color[1] * 255), int(color[2] * 255)
        return f'#{r:02x}{g:02x}{b:02x}'

    def on_key_press(self, event):
        """Обработка нажатий клавиш для управления игроком."""
        key = event.keysym.lower()
        if self.player:
            if key == 'w':
                self.player.move(0, 0, -self.move_speed)
            elif key == 's':
                self.player.move(0, 0, self.move_speed)
            elif key == 'a':
                self.player.move(-self.move_speed, 0, 0)
            elif key == 'd':
                self.player.move(self.move_speed, 0, 0)
            elif key == 'q':
                self.player.move(0, -self.move_speed, 0)
            elif key == 'e':
                self.player.move(0, self.move_speed, 0)

    def set_player(self, obj):
        """Устанавливает объект как управляемого игрока."""
        self.player = obj

    def run(self):
        """Запускает анимацию и главный цикл окна."""
        self.update()
        self.window.mainloop()

def create_cube(size=150, speed=0.01, position=(0, 0, 0), color="white", fill=False, outline_color="white", line_width=2, speed_x=None, speed_y=None, speed_z=None):
    """Создаёт куб с заданными параметрами."""
    points, edges, faces = create_cube_data(size)
    return Object3D(points, edges, faces, speed, position, color, fill, outline_color, line_width, speed_x, speed_y, speed_z)

def create_object_from_file(filename, **options):
    """Загружает модель из .obj и создает полностью готовый Object3D."""
    return create_object_from_file_base(filename, **options)

def quick_scene(*objects, width=600, height=600, title="3D Сцена", bg="black"):
    """Быстро создаёт сцену с объектами и запускает её. Камера управляется клавиатурой."""
    scene = Scene3D(width, height, title, bg)
    for obj in objects:
        scene.add_object(obj)
    scene.run()
