import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import math
from .utils import normalize_color, calculate_normal, generate_edges_from_faces, load_obj, create_cube as create_cube_data, create_object_from_file as create_object_from_file_base, COLOR_MAP

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
    def __init__(self, points, edges=None, faces=None, speed=0.01, position=(0, 0, 0),
                 color="white",  # <-- Теперь можно писать "white"
                 fill=False,
                 outline_color="white", # <-- И здесь тоже
                 line_width=2, speed_x=None, speed_y=None, speed_z=None):
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
        # Используем нашу новую функцию для конвертации
        self.color = normalize_color(color)
        self.fill = fill
        self.outline_color = normalize_color(outline_color)
        self.line_width = line_width  # Толщина линий рёбер

        # --- ИЗМЕНЕНИЯ ЗДЕСЬ ---
        # 1. Храним оригинальные, нетронутые нормали
        self.base_normals = []
        if self.faces:
            # Создаем numpy массив из точек для быстрых операций
            p_array = np.array(self.base_points)
            for face in self.faces:
                normal = calculate_normal(p_array[face[0]],
                                          p_array[face[1]],
                                          p_array[face[2]])
                self.base_normals.append(normal)

        # 2. Преобразуем в numpy array для векторных операций
        self.base_normals = np.array(self.base_normals, dtype=float)
        # 3. А этот массив будем изменять и отрисовывать каждый кадр
        self.normals = np.copy(self.base_normals)
        # --- КОНЕЦ ИЗМЕНЕНИЙ ---

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
        """Обновляет углы и поворачивает объект, исходя из ОРИГИНАЛЬНЫХ точек и нормалей."""
        if self.speed > 0 or self.speed_x > 0 or self.speed_y > 0 or self.speed_z > 0:
            self.angle_x += self.speed_x
            self.angle_y += self.speed_y
            self.angle_z += self.speed_z

            # --- ИЗМЕНЕНИЯ ЗДЕСЬ ---
            # Векторное вращение всех точек
            self.points = self.rotate_points(self.base_points, self.angle_x, self.angle_y, self.angle_z)
            # И ТОЧНО ТАКОЕ ЖЕ вращение для нормалей
            self.normals = self.rotate_points(self.base_normals, self.angle_x, self.angle_y, self.angle_z)
            # --- КОНЕЦ ИЗМЕНЕНИЙ ---

    def draw(self):
        """Отрисовка объекта с помощью OpenGL."""
        glPushAttrib(GL_CURRENT_BIT | GL_LINE_BIT)  # Сохраняем цвет и параметры линий
        glPushMatrix()

        # Применяем позицию
        glTranslatef(self.position[0], self.position[1], self.position[2])

        # Отрисовка граней (если есть и fill=True)
        if self.faces and self.fill:
            glColor3f(*self.color)
            glBegin(GL_QUADS)
            for face_idx, face in enumerate(self.faces):
                # Устанавливаем нормаль для грани
                normal = self.normals[face_idx]
                glNormal3fv(normal)
                # Просто перебираем вершины
                for vertex_index in face:
                    glVertex3fv(self.points[vertex_index])
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
        glPopAttrib()  # Восстанавливаем состояние

class Scene3D:
    """Класс для управления 3D сценой с OpenGL."""
    def __init__(self, width=800, height=600, title="3D Сцена", bg="black"): # <-- Теперь можно "black"
        self.width = width
        self.height = height
        # Конвертируем цвет фона
        self.bg = normalize_color(bg)
        self.objects = []
        self.player = None  # Управляемый объект
        self.move_speed = 10  # Скорость движения
        self.camera_distance = 500  # Расстояние камеры
        self.camera_yaw = 0  # Вращение камеры по горизонтали
        self.camera_pitch = 0  # Вращение камеры по вертикали
        self.mouse_sensitivity = 0.5  # Чувствительность мыши
        self.last_mouse_pos = None  # Последняя позиция мыши

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
        glEnable(GL_CULL_FACE)  # Отсечение задних граней для оптимизации
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_POSITION, [1, 1, 1, 0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [1, 1, 1, 1])
        glLightfv(GL_LIGHT0, GL_SPECULAR, [1, 1, 1, 1])  # Добавляем белый блик источнику света

        # Указываем, как материал должен блестеть
        glMaterialfv(GL_FRONT, GL_SPECULAR, [1, 1, 1, 1])  # Материал отражает белый блик
        glMaterialf(GL_FRONT, GL_SHININESS, 50)  # Резкость/размер блика (0-128)

        # --- ИСПРАВЛЕНИЕ ---
        # Разрешаем OpenGL использовать цвет из glColor как цвет материала
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)  # Управляем и фоновым цветом тоже

        # Автоматическая нормализация нормалей после трансформаций
        glEnable(GL_NORMALIZE)

        # Эту строку теперь можно удалить, так как цвет будет браться из glColor
        # glMaterialfv(GL_FRONT, GL_DIFFUSE, [1, 1, 1, 1])

    def add_object(self, obj):
        """Добавляет объект в сцену."""
        self.objects.append(obj)

    def update(self):
        """Главный цикл анимации."""
        # Очистка экрана
        glClearColor(*self.bg, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Настройка камеры с орбитальным управлением
        glLoadIdentity()
        # Сдвигаем камеру назад
        glTranslatef(0, 0, -self.camera_distance)
        # Вращаем сцену на основе движения мыши
        glRotatef(self.camera_pitch, 1, 0, 0)
        glRotatef(self.camera_yaw, 0, 1, 0)

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
                    # Управление относительно направления камеры
                    rad_yaw = math.radians(self.camera_yaw)
                    if event.key == pygame.K_w:
                        # Вперед относительно камеры
                        dx = -self.move_speed * math.sin(rad_yaw)
                        dz = -self.move_speed * math.cos(rad_yaw)
                        self.player.move(dx, 0, dz)
                    elif event.key == pygame.K_s:
                        # Назад относительно камеры
                        dx = self.move_speed * math.sin(rad_yaw)
                        dz = self.move_speed * math.cos(rad_yaw)
                        self.player.move(dx, 0, dz)
                    elif event.key == pygame.K_a:
                        # Влево относительно камеры
                        dx = -self.move_speed * math.cos(rad_yaw)
                        dz = self.move_speed * math.sin(rad_yaw)
                        self.player.move(dx, 0, dz)
                    elif event.key == pygame.K_d:
                        # Вправо относительно камеры
                        dx = self.move_speed * math.cos(rad_yaw)
                        dz = -self.move_speed * math.sin(rad_yaw)
                        self.player.move(dx, 0, dz)
                    elif event.key == pygame.K_q:
                        self.player.move(0, -self.move_speed, 0)
                    elif event.key == pygame.K_e:
                        self.player.move(0, self.move_speed, 0)
            elif event.type == pygame.MOUSEMOTION:
                if pygame.mouse.get_pressed()[0]:  # Если зажата левая кнопка
                    # event.rel содержит изменение позиции (dx, dy)
                    self.camera_yaw += event.rel[0] * self.mouse_sensitivity  # Регулируйте чувствительность
                    self.camera_pitch += event.rel[1] * self.mouse_sensitivity
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:  # Колесико вверх
                    self.camera_distance -= 20
                elif event.button == 5:  # Колесико вниз
                    self.camera_distance += 20
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

def create_cube(size=150, speed=0.01, position=(0, 0, 0), color="white", fill=False, outline_color="white", line_width=2, speed_x=None, speed_y=None, speed_z=None):
    """Создаёт куб с заданными параметрами."""
    points, edges, faces = create_cube_data(size)
    return Object3D(points, edges, faces, speed, position, color, fill, outline_color, line_width, speed_x, speed_y, speed_z)

def create_object_from_file(filename, **options):
    """Загружает модель из .obj и создает полностью готовый Object3D."""
    return create_object_from_file_base(filename, **options)

def quick_scene(*objects, width=800, height=600, title="3D Сцена", bg="black"):
    """Быстро создаёт сцену с объектами и запускает её."""
    scene = Scene3D(width, height, title, bg)
    for obj in objects:
        scene.add_object(obj)
    scene.run()
