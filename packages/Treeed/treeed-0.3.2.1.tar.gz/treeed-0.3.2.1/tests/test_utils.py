import pytest
import numpy as np
from py3dgraphics.utils import normalize_color, calculate_normal, generate_edges_from_faces, load_obj, create_cube, COLOR_MAP


def test_normalize_color_string():
    """Test normalize_color with string inputs."""
    assert normalize_color("red") == (1.0, 0.0, 0.0)
    assert normalize_color("white") == (1.0, 1.0, 1.0)
    assert normalize_color("black") == (0.0, 0.0, 0.0)


def test_normalize_color_tuple():
    """Test normalize_color with tuple inputs."""
    assert normalize_color((255, 0, 0)) == (1.0, 0.0, 0.0)
    assert normalize_color((0.5, 0.5, 0.5)) == (0.5, 0.5, 0.5)


def test_normalize_color_invalid():
    """Test normalize_color with invalid input."""
    assert normalize_color("invalid") == (1.0, 1.0, 1.0)  # Default white


def test_calculate_normal():
    """Test calculate_normal function."""
    p0 = [0, 0, 0]
    p1 = [1, 0, 0]
    p2 = [0, 1, 0]
    normal = calculate_normal(p0, p1, p2)
    assert len(normal) == 3
    assert abs(np.linalg.norm(normal) - 1.0) < 1e-6  # Should be normalized


def test_generate_edges_from_faces():
    """Test generate_edges_from_faces function."""
    faces = [(0, 1, 2), (1, 2, 3)]
    edges = generate_edges_from_faces(faces)
    expected_edges = {(0, 1), (1, 2), (0, 2), (2, 3), (1, 3)}
    assert set(edges) == expected_edges


def test_load_obj():
    """Test load_obj function with a simple cube.obj file."""
    # This would require a test obj file, but for now we'll skip
    pass


if __name__ == "__main__":
    pytest.main([__file__])
