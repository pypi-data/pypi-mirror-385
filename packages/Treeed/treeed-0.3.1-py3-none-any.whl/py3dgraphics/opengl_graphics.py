import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import math

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
    def __init__(self, points, edges=None, faces=None, speed=0.01, position=(0, 0, 0), color=(1.0, 1.0, 1.0), fill=False, outline_color=(1.0, 1.0, 1.0), line_width=2, speed_x=None, speed_y=None, speed_z=None):
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
        self.color = color  # Цвет заливки граней (RGB 0-1)
        self.fill = fill  # Флаг заливки граней
        self.outline_color = outline_color  # Цвет контура (RGB 0-1)
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

    def update_rotation(self):
        """Обновляет углы и поворачивает объект, исходя из ОРИГИНАЛЬНЫХ точек."""
        if self.speed > 0 or self.speed_x > 0 or self.speed_y > 0 or self.speed_z > 0:
            self.angle_x += self.speed_x
            self.angle_y += self.speed_y
            self.angle_z += self.speed_z

            # Векторное вращение всех точек
            self.points = self.rotate_points(self.base_points, self.angle_x, self.angle_y, self.angle_z)

    def draw(self):
        """Отрисовка объекта с помощью OpenGL."""
        glPushMatrix()

        # Применяем позицию
        glTranslatef(self.position[0], self.position[1], self.position[2])

        # Отрисовка граней (если есть и fill=True)
        if self.faces and self.fill:
            glColor3f(*self.color)
            glBegin(GL_TRIANGLES)
            for face in self.faces:
                if len(face) >= 3:
                    # Для каждой грани рисуем треугольники
                    for i in range(1, len(face) - 1):
                        # Первая вершина
                        p0 = self.points[face[0]]
                        glVertex3f(p0[0], p0[1], p0[2])
                        # Вторая вершина
                        p1 = self.points[face[i]]
                        glVertex3f(p1[0], p1[1], p1[2])
                        # Третья вершина
                        p2 = self.points[face[i + 1]]
                        glVertex3f(p2[0], p2[1], p2[2])
            glEnd()

        # Отрисовка рёбер (если есть)
        if self.edges:
            glColor3f(*self.outline_color)
            glLineWidth(self.line_width)
            glBegin(GL_LINES)
            for edge in self.edges:
                p1 = self.points[edge[0]]
                p2 = self.points[edge[1]]
                glVertex3f(p1[0], p1[1], p1[2])
                glVertex3f(p2[0], p2[1], p2[2])
            glEnd()

        glPopMatrix()

class Scene3D:
    """Класс для управления 3D сценой с OpenGL."""
    def __init__(self, width=800, height=600, title="3D Сцена", bg=(0.0, 0.0, 0.0)):
        self.width = width
        self.height = height
        self.bg = bg
        self.objects = []
        self.player = None  # Управляемый объект
        self.move_speed = 10  # Скорость движения
        self.camera_distance = 500  # Расстояние камеры
        self.camera_angle_x = 0
        self.camera_angle_y = 0

        # Инициализация Pygame и OpenGL
        pygame.init()
        pygame.display.set_mode((width, height), pygame.DOUBLEBUF | pygame.OPENGL)
        pygame.display.set_caption(title)

        # Настройка OpenGL
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, (width / height), 0.1, 1000.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # Настройка освещения
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_POSITION, [1, 1, 1, 0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [1, 1, 1, 1])

        # Настройка материала
        glMaterialfv(GL_FRONT, GL_DIFFUSE, [1, 1, 1, 1])

    def add_object(self, obj):
        """Добавляет объект в сцену."""
        self.objects.append(obj)

    def update(self):
        """Главный цикл анимации."""
        # Очистка экрана
        glClearColor(*self.bg, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Настройка камеры
        glLoadIdentity()
        gluLookAt(0, 0, self.camera_distance,
                  0, 0, 0,
                  0, 1, 0)

        # Обновление и отрисовка объектов
        for obj in self.objects:
            obj.update_rotation()
            obj.draw()

        pygame.display.flip()

    def handle_events(self):
        """Обработка событий Pygame."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif self.player:
                    if event.key == pygame.K_w:
                        self.player.move(0, 0, -self.move_speed)
                    elif event.key == pygame.K_s:
                        self.player.move(0, 0, self.move_speed)
                    elif event.key == pygame.K_a:
                        self.player.move(-self.move_speed, 0, 0)
                    elif event.key == pygame.K_d:
                        self.player.move(self.move_speed, 0, 0)
                    elif event.key == pygame.K_q:
                        self.player.move(0, -self.move_speed, 0)
                    elif event.key == pygame.K_e:
                        self.player.move(0, self.move_speed, 0)
        return True

    def set_player(self, obj):
        """Устанавливает объект как управляемого игрока."""
        self.player = obj

    def run(self):
        """Запускает главный цикл сцены."""
        clock = pygame.time.Clock()
        running = True
        while running:
            running = self.handle_events()
            self.update()
            clock.tick(60)  # 60 FPS

        pygame.quit()

def create_cube(size=150, speed=0.01, position=(0, 0, 0), color=(1.0, 1.0, 1.0), fill=False, outline_color=(1.0, 1.0, 1.0), line_width=2, speed_x=None, speed_y=None, speed_z=None):
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
        (0, 1, 2, 3),  # Задняя грань
        (4, 5, 6, 7),  # Передняя грань
        (0, 4, 7, 3),  # Левая грань
        (1, 5, 6, 2),  # Правая грань
        (0, 1, 5, 4),  # Нижняя грань
        (3, 2, 6, 7)   # Верхняя грань
    ]
    return Object3D(points, edges, faces, speed, position, color, fill, outline_color, line_width, speed_x, speed_y, speed_z)

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

def create_object_from_file(filename, **options):
    """Загружает модель из .obj и создает полностью готовый Object3D."""
    points, faces = load_obj(filename)
    if not points or not faces:
        return None  # Возвращаем None, если файл пуст или некорректен

    edges = generate_edges_from_faces(faces)

    # Создаем объект, передавая ему и грани, и сгенерированные рёбра
    return Object3D(points, edges=edges, faces=faces, **options)

def quick_scene(*objects, width=800, height=600, title="3D Сцена", bg=(0.0, 0.0, 0.0)):
    """Быстро создаёт сцену с объектами и запускает её."""
    scene = Scene3D(width, height, title, bg)
    for obj in objects:
        scene.add_object(obj)
    scene.run()
