import pytest
import os
import numpy as np

# Set engine to PyOpenGL for testing
os.environ['PY3D_ENGINE'] = '3'
from py3dgraphics.opengl_graphics import Point3D, Object3D, Scene3D, create_cube


def test_point3d():
    """Test Point3D class."""
    p = Point3D(1, 2, 3)
    assert p.x == 1
    assert p.y == 2
    assert p.z == 3
    assert p.to_list() == [1, 2, 3]


def test_object3d_init():
    """Test Object3D initialization."""
    points = [[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]]
    obj = Object3D(points)
    assert np.array_equal(obj.base_points, np.array(points))
    assert obj.edges is None
    assert obj.faces is None


def test_object3d_set_position():
    """Test Object3D set_position method."""
    points = [[0, 0, 0], [1, 0, 0]]
    obj = Object3D(points)
    obj.set_position(10, 20, 30)
    assert np.array_equal(obj.position, np.array([10, 20, 30]))


def test_object3d_move():
    """Test Object3D move method."""
    points = [[0, 0, 0], [1, 0, 0]]
    obj = Object3D(points, position=(0, 0, 0))
    obj.move(5, 10, 15)
    assert np.array_equal(obj.position, np.array([5, 10, 15]))


def test_create_cube():
    """Test create_cube function."""
    cube = create_cube(size=50)
    assert isinstance(cube, Object3D)
    assert len(cube.points) == 8
    assert len(cube.edges) == 12
    assert len(cube.faces) == 6


def test_create_cube_data():
    """Test create_cube function data."""
    cube = create_cube(100)
    assert len(cube.base_points) == 8
    assert len(cube.edges) == 12
    assert len(cube.faces) == 6
    # Check that points are correct for size 100
    assert np.array_equal(cube.base_points[0], [-100.0, -100.0, -100.0])
    assert np.array_equal(cube.base_points[7], [-100.0, 100.0, 100.0])


@pytest.mark.skip(reason="Cannot run tkinter tests in a non-GUI environment")
def test_scene3d_init():
    """Test Scene3D initialization."""
    scene = Scene3D(width=400, height=300, title="Test Scene")
    assert scene.width == 400
    assert scene.height == 300
    assert scene.objects == []


@pytest.mark.skip(reason="Cannot run pygame GUI tests in a non-GUI environment")
def test_scene3d_add_object():
    """Test Scene3D add_object method."""
    scene = Scene3D()
    obj = Object3D([[0, 0, 0]])
    scene.add_object(obj)
    assert len(scene.objects) == 1
    assert scene.objects[0] is obj


if __name__ == "__main__":
    pytest.main([__file__])
