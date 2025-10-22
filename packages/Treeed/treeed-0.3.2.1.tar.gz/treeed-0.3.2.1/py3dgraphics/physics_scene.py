"""
Модуль для физической симуляции с использованием PyBullet.
PhysicsScene - класс сцены с поддержкой физики.
"""

import time
import numpy as np
try:
    import pybullet as p
    import pybullet_data
    PYBULLET_AVAILABLE = True
except ImportError:
    PYBULLET_AVAILABLE = False
    print("PyBullet не установлен. Физическая симуляция недоступна.")

from .opengl_graphics import Scene3D, Object3D, Point3D


class PhysicsScene(Scene3D):
    """
    Сцена с поддержкой физической симуляции через PyBullet.

    Наследуется от Scene3D и добавляет физические свойства объектам.
    """

    def __init__(self, width=800, height=600, title="Physics Scene", bg=(0.0, 0.0, 0.0),
                 gravity=(0, 0, -9.81), time_step=1/240.0):
        """
        Инициализация физической сцены.

        Args:
            width, height: Размеры окна
            title: Заголовок окна
            bg: Цвет фона
            gravity: Вектор гравитации (x, y, z)
            time_step: Шаг симуляции в секундах
        """
        if not PYBULLET_AVAILABLE:
            raise ImportError("PyBullet не установлен. Установите с 'pip install treeed[physics]'")

        super().__init__(width, height, title, bg)

        # Инициализация PyBullet
        p.connect(p.DIRECT)  # Используем DIRECT mode для интеграции с OpenGL
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setGravity(*gravity)
        p.setTimeStep(time_step)

        # Загружаем плоскость для земли
        self.plane_id = p.loadURDF("plane.urdf")

        # Словарь для хранения соответствия между Object3D и PyBullet body IDs
        self.physics_bodies = {}

        # Настройки физики
        self.gravity = gravity
        self.time_step = time_step
        self.paused = False

    def add_physics_object(self, obj, mass=1.0, friction=0.5, restitution=0.1):
        """
        Добавляет объект с физическими свойствами.

        Args:
            obj: Object3D для добавления
            mass: Масса объекта (0 для статических объектов)
            friction: Коэффициент трения
            restitution: Коэффициент упругости (отскока)
        """
        # Добавляем объект в сцену
        self.add_object(obj)

        # Создаем collision shape из точек объекта
        if obj.faces:
            # Используем convex hull для сложных объектов
            points = np.array(obj.points)
            collision_shape = p.createCollisionShape(p.GEOM_CONVEX_HULL, points=points.flatten())
        else:
            # Для простых объектов используем box
            size = np.ptp(obj.points, axis=0) / 2  # Размер по осям
            collision_shape = p.createCollisionShape(p.GEOM_BOX, halfExtents=size)

        # Создаем rigid body
        position = obj.position
        orientation = p.getQuaternionFromEuler([0, 0, 0])  # Начальная ориентация

        body_id = p.createMultiBody(
            baseMass=mass,
            baseCollisionShapeIndex=collision_shape,
            basePosition=position,
            baseOrientation=orientation
        )

        # Устанавливаем физические свойства
        p.changeDynamics(body_id, -1, lateralFriction=friction, restitution=restitution)

        # Сохраняем соответствие
        self.physics_bodies[obj] = body_id

    def add_cube_physics(self, size=100, position=(0, 0, 200), mass=1.0, color=(1.0, 0.0, 0.0),
                        speed=0.01, friction=0.5, restitution=0.1):
        """
        Создает куб с физическими свойствами.

        Args:
            size: Размер куба
            position: Начальная позиция
            mass: Масса
            color: Цвет
            speed: Скорость вращения (для визуализации)
            friction: Трение
            restitution: Упругость

        Returns:
            Object3D: Созданный объект
        """
        # Создаем визуальный объект
        cube = self.create_cube(size=size, position=position, color=color, speed=speed, fill=True)

        # Добавляем физические свойства
        self.add_physics_object(cube, mass=mass, friction=friction, restitution=restitution)

        return cube

    def apply_force(self, obj, force=(0, 0, 0), position=None):
        """
        Применяет силу к объекту.

        Args:
            obj: Object3D
            force: Вектор силы (x, y, z)
            position: Позиция приложения силы (центр масс по умолчанию)
        """
        if obj in self.physics_bodies:
            body_id = self.physics_bodies[obj]
            if position is None:
                position = obj.position
            p.applyExternalForce(body_id, -1, force, position, p.WORLD_FRAME)

    def apply_torque(self, obj, torque=(0, 0, 0)):
        """
        Применяет крутящий момент к объекту.

        Args:
            obj: Object3D
            torque: Вектор момента (x, y, z)
        """
        if obj in self.physics_bodies:
            body_id = self.physics_bodies[obj]
            p.applyExternalTorque(body_id, -1, torque, p.WORLD_FRAME)

    def set_velocity(self, obj, linear_velocity=(0, 0, 0), angular_velocity=(0, 0, 0)):
        """
        Устанавливает скорость объекту.

        Args:
            obj: Object3D
            linear_velocity: Линейная скорость (x, y, z)
            angular_velocity: Угловую скорость (x, y, z)
        """
        if obj in self.physics_bodies:
            body_id = self.physics_bodies[obj]
            p.resetBaseVelocity(body_id, linearVelocity=linear_velocity, angularVelocity=angular_velocity)

    def update_physics(self):
        """
        Обновляет состояние физической симуляции.
        """
        if not self.paused:
            p.stepSimulation()

            # Синхронизируем позиции и ориентации объектов
            for obj, body_id in self.physics_bodies.items():
                pos, orn = p.getBasePositionAndOrientation(body_id)
                obj.set_position(*pos)

                # Конвертируем кватернион в углы Эйлера для вращения
                euler = p.getEulerFromQuaternion(orn)
                # Обновляем вращение объекта (упрощенная версия)
                obj.rotation_x = euler[0]
                obj.rotation_y = euler[1]
                obj.rotation_z = euler[2]

    def toggle_pause(self):
        """Переключает паузу симуляции."""
        self.paused = not self.paused

    def reset_simulation(self):
        """
        Сбрасывает симуляцию в начальное состояние.
        """
        # Сбрасываем все объекты в начальные позиции
        for obj, body_id in self.physics_bodies.items():
            p.resetBasePositionAndOrientation(body_id, obj.position, [0, 0, 0, 1])
            p.resetBaseVelocity(body_id, [0, 0, 0], [0, 0, 0])

    def run_physics(self, max_steps=None):
        """
        Запускает цикл симуляции с физикой.

        Args:
            max_steps: Максимальное количество шагов (None для бесконечного цикла)
        """
        step = 0
        while max_steps is None or step < max_steps:
            self.update_physics()
            self.update_scene()

            # Обработка событий
            for event in self.pygame_events():
                if event.type == self.pygame.QUIT:
                    return
                elif event.type == self.pygame.KEYDOWN:
                    if event.key == self.pygame.K_SPACE:
                        self.toggle_pause()
                    elif event.key == self.pygame.K_r:
                        self.reset_simulation()
                    elif event.key == self.pygame.K_ESCAPE:
                        return

            step += 1
            time.sleep(self.time_step)

    def __del__(self):
        """Очистка ресурсов PyBullet."""
        if PYBULLET_AVAILABLE:
            p.disconnect()


# Функции для создания объектов с физикой
def create_physics_cube(size=100, position=(0, 0, 200), mass=1.0, color=(1.0, 0.0, 0.0),
                       friction=0.5, restitution=0.1):
    """
    Создает куб для использования в физической сцене.

    Returns:
        Object3D: Куб с настройками для физики
    """
    from .utils import create_cube
    return create_cube(size=size, position=position, color=color, speed=0, fill=True)


def quick_physics_scene(*objects, width=800, height=600, title="Physics Scene",
                       bg=(0.0, 0.0, 0.0), gravity=(0, 0, -9.81)):
    """
    Быстро создает и запускает физическую сцену.

    Args:
        *objects: Объекты для добавления (должны быть Object3D)
        width, height: Размеры окна
        title: Заголовок
        bg: Цвет фона
        gravity: Вектор гравитации
    """
    scene = PhysicsScene(width=width, height=height, title=title, bg=bg, gravity=gravity)

    for obj in objects:
        scene.add_physics_object(obj)

    scene.run_physics()
