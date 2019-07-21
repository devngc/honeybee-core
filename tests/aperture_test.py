"""Test the Aperture class."""
from honeybee.aperture import Aperture
from honeybee.shade import Shade
from honeybee.boundarycondition import Outdoors
from honeybee.aperturetype import Window

from ladybug_geometry.geometry3d.face import Face3D
from ladybug_geometry.geometry3d.plane import Plane
from ladybug_geometry.geometry3d.pointvector import Point3D, Vector3D

import pytest


def test_aperture_init():
    """Test the initialization of Aperture objects."""
    pts = (Point3D(0, 0, 0), Point3D(0, 0, 3), Point3D(5, 0, 3), Point3D(5, 0, 0))
    aperture = Aperture('Test Window', Face3D(pts))
    str(aperture)  # test the string representation

    assert aperture.name == 'TestWindow'
    assert aperture.name_original == 'Test Window'
    assert isinstance(aperture.geometry, Face3D)
    assert len(aperture.vertices) == 4
    assert aperture.upper_left_vertices[0] == Point3D(5, 0, 3)
    assert len(aperture.triangulated_mesh3d.faces) == 2
    assert aperture.normal == Vector3D(0, 1, 0)
    assert aperture.center == Point3D(2.5, 0, 1.5)
    assert aperture.area == 15
    assert aperture.perimeter == 16
    assert isinstance(aperture.boundary_condition, Outdoors)
    assert isinstance(aperture.type, Window)
    assert not aperture.has_parent


def test_aperture_from_vertices():
    """Test the initialization of Aperture objects from vertices."""
    pts = (Point3D(0, 0, 0), Point3D(0, 0, 3), Point3D(5, 0, 3), Point3D(5, 0, 0))
    aperture = Aperture.from_vertices('Test Window', pts)

    assert aperture.name == 'TestWindow'
    assert aperture.name_original == 'Test Window'
    assert isinstance(aperture.geometry, Face3D)
    assert len(aperture.vertices) == 4
    assert aperture.upper_left_vertices[0] == Point3D(5, 0, 3)
    assert len(aperture.triangulated_mesh3d.faces) == 2
    assert aperture.normal == Vector3D(0, 1, 0)
    assert aperture.center == Point3D(2.5, 0, 1.5)
    assert aperture.area == 15
    assert aperture.perimeter == 16
    assert isinstance(aperture.boundary_condition, Outdoors)
    assert isinstance(aperture.type, Window)
    assert not aperture.has_parent


def test_aperture_duplicate():
    """Test the duplication of Aperture objects."""
    pts = (Point3D(0, 0, 0), Point3D(0, 0, 3), Point3D(5, 0, 3), Point3D(5, 0, 0))
    ap_1 = Aperture('Test Window', Face3D(pts))
    ap_2 = ap_1.duplicate()

    assert ap_1 is not ap_2
    for i, pt in enumerate(ap_1.vertices):
        assert pt == ap_2.vertices[i]
    assert ap_1.name == ap_2.name

    ap_2.move(Vector3D(0, 1, 0))
    for i, pt in enumerate(ap_1.vertices):
        assert pt != ap_2.vertices[i]


def test_aperture_overhang():
    """Test the creation of an overhang for Aperture objects."""
    pts_1 = (Point3D(0, 0, 0), Point3D(0, 0, 3), Point3D(5, 0, 3), Point3D(5, 0, 0))
    pts_2 = (Point3D(0, 0, 0), Point3D(2, 0, 3), Point3D(4, 0, 3))
    pts_3 = (Point3D(0, 0, 0), Point3D(2, 0, 3), Point3D(4, 0, 0))
    aperture_1 = Aperture('Rectangle Window', Face3D(pts_1))
    aperture_2 = Aperture('Good Triangle Window', Face3D(pts_2))
    aperture_3 = Aperture('Bad Triangle Window', Face3D(pts_3))
    overhang_1 = aperture_1.overhang(1, tolerance=0.01)
    overhang_2 = aperture_2.overhang(1, tolerance=0.01)
    overhang_3 = aperture_3.overhang(1, tolerance=0.01)
    assert isinstance(overhang_1, Shade)
    assert isinstance(overhang_2, Shade)
    assert overhang_3 is None


def test_aperture_fin():
    """Test the creation of a fins for Aperture objects."""
    pts_1 = (Point3D(0, 0, 0), Point3D(0, 0, 3), Point3D(5, 0, 3), Point3D(5, 0, 0))
    pts_2 = (Point3D(0, 0, 0), Point3D(2, 0, 3), Point3D(4, 0, 3))
    aperture_1 = Aperture('Rectangle Window', Face3D(pts_1))
    aperture_2 = Aperture('Triangle Window', Face3D(pts_2))
    right_fin_1 = aperture_1.right_fin(1, tolerance=0.01)
    right_fin_2 = aperture_2.right_fin(1, tolerance=0.01)
    left_fin_1 = aperture_1.left_fin(1, tolerance=0.01)
    left_fin_2 = aperture_2.left_fin(1, tolerance=0.01)
    assert isinstance(right_fin_1, Shade)
    assert right_fin_2 is None
    assert isinstance(left_fin_1, Shade)
    assert left_fin_2 is None


def test_aperture_extruded_border():
    """Test the creation of an extruded border for Aperture objects."""
    pts_1 = (Point3D(0, 0, 0), Point3D(0, 0, 3), Point3D(5, 0, 3), Point3D(5, 0, 0))
    pts_2 = (Point3D(0, 0, 0), Point3D(2, 0, 3), Point3D(4, 0, 3))
    aperture_1 = Aperture('Rectangle Window', Face3D(pts_1))
    aperture_2 = Aperture('Triangle Window', Face3D(pts_2))

    border_1_out = aperture_1.extruded_border(0.1)
    border_2_out = aperture_2.extruded_border(0.1)
    border_1_in = aperture_1.extruded_border(0.1, True)
    border_2_in = aperture_2.extruded_border(0.1, True)

    assert len(border_1_out) == 4
    assert border_1_out[0].center.y > 0
    assert len(border_2_out) == 3
    assert border_2_out[0].center.y > 0
    assert len(border_1_in) == 4
    assert border_1_in[0].center.y < 0
    assert len(border_2_in) == 3
    assert border_2_in[0].center.y < 0


def test_aperture_louvers_by_distance_between():
    """Test the creation of a louvers_by_distance_between for Aperture objects."""
    pts_1 = (Point3D(0, 0, 0), Point3D(0, 0, 3), Point3D(5, 0, 3), Point3D(5, 0, 0))
    aperture = Aperture('Rectangle Window', Face3D(pts_1))
    louvers = aperture.louvers_by_distance_between(0.5, 0.2, 0.1)

    assert len(louvers) == 6
    for louver in louvers:
        assert isinstance(louver, Shade)
        assert louver.area == 5 * 0.2


def test_move():
    """Test the Aperture move method."""
    pts_1 = (Point3D(0, 0, 0), Point3D(2, 0, 0), Point3D(2, 2, 0), Point3D(0, 2, 0))
    plane_1 = Plane(Vector3D(0, 0, 1), Point3D(0, 0, 0))
    aperture = Aperture('Rectangle Window', Face3D(pts_1, plane_1))

    vec_1 = Vector3D(2, 2, 2)
    new_ap = aperture.duplicate()
    new_ap.move(vec_1)
    assert new_ap.geometry[0] == Point3D(2, 2, 2)
    assert new_ap.geometry[1] == Point3D(4, 2, 2)
    assert new_ap.geometry[2] == Point3D(4, 4, 2)
    assert new_ap.geometry[3] == Point3D(2, 4, 2)
    assert new_ap.normal == aperture.normal
    assert aperture.area == new_ap.area
    assert aperture.perimeter == new_ap.perimeter


def test_scale():
    """Test the Aperture scale method."""
    pts = (Point3D(1, 1, 2), Point3D(2, 1, 2), Point3D(2, 2, 2), Point3D(1, 2, 2))
    plane = Plane(Vector3D(0, 0, 1), Point3D(0, 0, 2))
    aperture = Aperture('Rectangle Window', Face3D(pts, plane))

    new_ap = aperture.duplicate()
    new_ap.scale(2)
    assert new_ap.geometry[0] == Point3D(2, 2, 4)
    assert new_ap.geometry[1] == Point3D(4, 2, 4)
    assert new_ap.geometry[2] == Point3D(4, 4, 4)
    assert new_ap.geometry[3] == Point3D(2, 4, 4)
    assert new_ap.area == aperture.area * 2 ** 2
    assert new_ap.perimeter == aperture.perimeter * 2
    assert new_ap.normal == aperture.normal


def test_rotate():
    """Test the Aperture rotate method."""
    pts = (Point3D(0, 0, 2), Point3D(2, 0, 2), Point3D(2, 2, 2), Point3D(0, 2, 2))
    plane = Plane(Vector3D(0, 0, 1), Point3D(0, 0, 2))
    aperture = Aperture('Rectangle Window', Face3D(pts, plane))
    origin = Point3D(0, 0, 0)
    axis = Vector3D(1, 0, 0)

    test_1 = aperture.duplicate()
    test_1.rotate(axis, 180, origin)
    assert test_1.geometry[0].x == pytest.approx(0, rel=1e-3)
    assert test_1.geometry[0].y == pytest.approx(0, rel=1e-3)
    assert test_1.geometry[0].z == pytest.approx(-2, rel=1e-3)
    assert test_1.geometry[2].x == pytest.approx(2, rel=1e-3)
    assert test_1.geometry[2].y == pytest.approx(-2, rel=1e-3)
    assert test_1.geometry[2].z == pytest.approx(-2, rel=1e-3)
    assert aperture.area == test_1.area
    assert len(aperture.vertices) == len(test_1.vertices)

    test_2 = aperture.duplicate()
    test_2.rotate(axis, 90, origin)
    assert test_2.geometry[0].x == pytest.approx(0, rel=1e-3)
    assert test_2.geometry[0].y == pytest.approx(-2, rel=1e-3)
    assert test_2.geometry[0].z == pytest.approx(0, rel=1e-3)
    assert test_2.geometry[2].x == pytest.approx(2, rel=1e-3)
    assert test_2.geometry[2].y == pytest.approx(-2, rel=1e-3)
    assert test_2.geometry[2].z == pytest.approx(2, rel=1e-3)
    assert aperture.area == test_2.area
    assert len(aperture.vertices) == len(test_2.vertices)


def test_rotate_xy():
    """Test the Aperture rotate_xy method."""
    pts = (Point3D(1, 1, 2), Point3D(2, 1, 2), Point3D(2, 2, 2), Point3D(1, 2, 2))
    plane = Plane(Vector3D(0, 0, 1), Point3D(0, 0, 2))
    aperture = Aperture('Rectangle Window', Face3D(pts, plane))
    origin_1 = Point3D(1, 1, 0)

    test_1 = aperture.duplicate()
    test_1.rotate_xy(180, origin_1)
    assert test_1.geometry[0].x == pytest.approx(1, rel=1e-3)
    assert test_1.geometry[0].y == pytest.approx(1, rel=1e-3)
    assert test_1.geometry[0].z == pytest.approx(2, rel=1e-3)
    assert test_1.geometry[2].x == pytest.approx(0, rel=1e-3)
    assert test_1.geometry[2].y == pytest.approx(0, rel=1e-3)
    assert test_1.geometry[2].z == pytest.approx(2, rel=1e-3)

    test_2 = aperture.duplicate()
    test_2.rotate_xy(90, origin_1)
    assert test_2.geometry[0].x == pytest.approx(1, rel=1e-3)
    assert test_2.geometry[0].y == pytest.approx(1, rel=1e-3)
    assert test_1.geometry[0].z == pytest.approx(2, rel=1e-3)
    assert test_2.geometry[2].x == pytest.approx(0, rel=1e-3)
    assert test_2.geometry[2].y == pytest.approx(2, rel=1e-3)
    assert test_1.geometry[2].z == pytest.approx(2, rel=1e-3)


def test_reflect():
    """Test the Aperture reflect method."""
    pts = (Point3D(1, 1, 2), Point3D(2, 1, 2), Point3D(2, 2, 2), Point3D(1, 2, 2))
    plane = Plane(Vector3D(0, 0, 1), Point3D(0, 0, 2))
    aperture = Aperture('Rectangle Window', Face3D(pts, plane))

    origin_1 = Point3D(1, 0, 2)
    origin_2 = Point3D(0, 0, 2)
    normal_1 = Vector3D(1, 0, 0)
    normal_2 = Vector3D(-1, -1, 0).normalize()
    plane_1 = Plane(normal_1, origin_1)
    plane_2 = Plane(normal_2, origin_2)
    plane_3 = Plane(normal_2, origin_1)

    test_1 = aperture.duplicate()
    test_1.reflect(plane_1)
    assert test_1.geometry[-1].x == pytest.approx(1, rel=1e-3)
    assert test_1.geometry[-1].y == pytest.approx(1, rel=1e-3)
    assert test_1.geometry[-1].z == pytest.approx(2, rel=1e-3)
    assert test_1.geometry[1].x == pytest.approx(0, rel=1e-3)
    assert test_1.geometry[1].y == pytest.approx(2, rel=1e-3)
    assert test_1.geometry[1].z == pytest.approx(2, rel=1e-3)

    test_1 = aperture.duplicate()
    test_1.reflect(plane_2)
    assert test_1.geometry[-1].x == pytest.approx(-1, rel=1e-3)
    assert test_1.geometry[-1].y == pytest.approx(-1, rel=1e-3)
    assert test_1.geometry[-1].z == pytest.approx(2, rel=1e-3)
    assert test_1.geometry[1].x == pytest.approx(-2, rel=1e-3)
    assert test_1.geometry[1].y == pytest.approx(-2, rel=1e-3)
    assert test_1.geometry[1].z == pytest.approx(2, rel=1e-3)

    test_2 = aperture.duplicate()
    test_2.reflect(plane_3)
    assert test_2.geometry[-1].x == pytest.approx(0, rel=1e-3)
    assert test_2.geometry[-1].y == pytest.approx(0, rel=1e-3)
    assert test_2.geometry[-1].z == pytest.approx(2, rel=1e-3)
    assert test_2.geometry[1].x == pytest.approx(-1, rel=1e-3)
    assert test_2.geometry[1].y == pytest.approx(-1, rel=1e-3)
    assert test_2.geometry[1].z == pytest.approx(2, rel=1e-3)


def test_check_planar():
    """Test the check_planar method."""
    pts_1 = (Point3D(0, 0, 2), Point3D(2, 0, 2), Point3D(2, 2, 2), Point3D(0, 2, 2))
    pts_2 = (Point3D(0, 0, 0), Point3D(2, 0, 2), Point3D(2, 2, 2), Point3D(0, 2, 2))
    pts_3 = (Point3D(0, 0, 2.0001), Point3D(2, 0, 2), Point3D(2, 2, 2), Point3D(0, 2, 2))
    plane_1 = Plane(Vector3D(0, 0, 1), Point3D(0, 0, 2))
    aperture_1 = Aperture('Window 1', Face3D(pts_1, plane_1))
    aperture_2 = Aperture('Window 2', Face3D(pts_2, plane_1))
    aperture_3 = Aperture('Window 3', Face3D(pts_3, plane_1))

    assert aperture_1.check_planar(0.001) is True
    assert aperture_2.check_planar(0.001, False) is False
    with pytest.raises(Exception):
        aperture_2.check_planar(0.0001)
    assert aperture_3.check_planar(0.001) is True
    assert aperture_3.check_planar(0.000001, False) is False
    with pytest.raises(Exception):
        aperture_3.check_planar(0.000001)


def test_check_self_intersecting():
    """Test the check_self_intersecting method."""
    plane_1 = Plane(Vector3D(0, 0, 1))
    plane_2 = Plane(Vector3D(0, 0, -1))
    pts_1 = (Point3D(0, 0), Point3D(2, 0), Point3D(2, 2), Point3D(0, 2))
    pts_2 = (Point3D(0, 0), Point3D(0, 2), Point3D(2, 0), Point3D(2, 2))
    aperture_1 = Aperture('Window 1', Face3D(pts_1, plane_1))
    aperture_2 = Aperture('Window 2', Face3D(pts_2, plane_1))
    aperture_3 = Aperture('Window 3', Face3D(pts_1, plane_2))
    aperture_4 = Aperture('Window 4', Face3D(pts_2, plane_2))

    assert aperture_1.check_self_intersecting(False) is True
    assert aperture_2.check_self_intersecting(False) is False
    with pytest.raises(Exception):
        assert aperture_2.check_self_intersecting(True)
    assert aperture_3.check_self_intersecting(False) is True
    assert aperture_4.check_self_intersecting(False) is False
    with pytest.raises(Exception):
        assert aperture_4.check_self_intersecting(True)


def test_check_non_zero():
    """Test the check_non_zero method."""
    plane_1 = Plane(Vector3D(0, 0, 1))
    pts_1 = (Point3D(0, 0), Point3D(2, 0), Point3D(2, 2))
    pts_2 = (Point3D(0, 0), Point3D(2, 0), Point3D(2, 0))
    aperture_1 = Aperture('Window 1', Face3D(pts_1, plane_1))
    aperture_2 = Aperture('Window 2', Face3D(pts_2, plane_1))

    assert aperture_1.check_non_zero(0.0001, False) is True
    assert aperture_2.check_non_zero(0.0001, False) is False
    with pytest.raises(Exception):
        assert aperture_2.check_self_intersecting(0.0001, True)


def test_to_dict():
    """Test the Aperture to_dict method."""
    vertices = [[0, 0, 0], [0, 10, 0], [0, 10, 3], [0, 0, 3]]
    ap = Aperture.from_vertices('Rectangle Window', vertices)

    ad = ap.to_dict()
    assert ad['type'] == 'Aperture'
    assert ad['name'] == 'RectangleWindow'
    assert ad['name_original'] == 'Rectangle Window'
    assert 'geometry' in ad
    assert len(ad['geometry']['boundary']) == len(vertices)
    assert 'properties' in ad
    assert ad['properties']['type'] == 'ApertureProperties'
    assert ad['aperture_type']['type'] == 'Window'
    assert ad['boundary_condition']['type'] == 'Outdoors'
    assert ad['parent'] is None