# Copyright (c) 2018-2020, Manfred Moitzi
# License: MIT License

import pytest
import ezdxf
import math
from ezdxf.math import (
    ConstructionArc,
    ConstructionCircle,
    ConstructionLine,
    UCS,
    Vec3,
    Vec2,
    arc_segment_count,
    arc_chord_length,
)
from math import isclose


def test_arc_from_2p_angle_complex():
    p1 = (-15.73335, 10.98719)
    p2 = (-12.67722, 8.76554)
    angle = 55.247230
    arc = ConstructionArc.from_2p_angle(start_point=p1, end_point=p2, angle=angle)

    arc_result = ConstructionArc(
        center=(-12.08260, 12.79635),
        radius=4.07443,
        start_angle=-153.638906,
        end_angle=-98.391676,
    )

    assert arc.center.isclose(arc_result.center, abs_tol=1e-5)
    assert isclose(arc.radius, arc_result.radius, abs_tol=1e-5)
    assert isclose(arc.start_angle, arc_result.start_angle, abs_tol=1e-4)
    assert isclose(arc.end_angle, arc_result.end_angle, abs_tol=1e-4)


def test_arc_from_2p_angle_simple():
    p1 = (2, 1)
    p2 = (0, 3)
    angle = 90

    arc = ConstructionArc.from_2p_angle(start_point=p1, end_point=p2, angle=angle)
    assert arc.center.isclose((0, 1))
    assert isclose(arc.radius, 2)
    assert isclose(arc.start_angle, 0, abs_tol=1e-12)
    assert isclose(arc.end_angle, 90)

    arc = ConstructionArc.from_2p_angle(start_point=p2, end_point=p1, angle=angle)
    assert arc.center.isclose((2, 3))
    assert isclose(arc.radius, 2)
    assert isclose(arc.start_angle, 180)
    assert isclose(arc.end_angle, -90)


def test_arc_from_2p_radius():
    p1 = (2, 1)
    p2 = (0, 3)
    radius = 2

    arc = ConstructionArc.from_2p_radius(start_point=p1, end_point=p2, radius=radius)
    assert arc.center.isclose((0, 1))
    assert isclose(arc.radius, radius)
    assert isclose(arc.start_angle, 0)
    assert isclose(arc.end_angle, 90)

    arc = ConstructionArc.from_2p_radius(start_point=p2, end_point=p1, radius=radius)
    assert arc.center.isclose((2, 3))
    assert isclose(arc.radius, radius)
    assert isclose(arc.start_angle, 180)
    assert isclose(arc.end_angle, -90)


def test_arc_from_3p():
    p1 = (-15.73335, 10.98719)
    p2 = (-12.67722, 8.76554)
    p3 = (-8.00817, 12.79635)
    arc = ConstructionArc.from_3p(start_point=p1, end_point=p2, def_point=p3)

    arc_result = ConstructionArc(
        center=(-12.08260, 12.79635),
        radius=4.07443,
        start_angle=-153.638906,
        end_angle=-98.391676,
    )

    assert arc.center.isclose(arc_result.center, abs_tol=1e-5)
    assert isclose(arc.radius, arc_result.radius, abs_tol=1e-5)
    assert isclose(arc.start_angle, arc_result.start_angle, abs_tol=1e-4)
    assert isclose(arc.end_angle, arc_result.end_angle, abs_tol=1e-4)


def test_spatial_arc_from_3p():
    start_point_wcs = Vec3(0, 1, 0)
    end_point_wcs = Vec3(1, 0, 0)
    def_point_wcs = Vec3(0, 0, 1)

    ucs = UCS.from_x_axis_and_point_in_xy(
        origin=def_point_wcs,
        axis=end_point_wcs - def_point_wcs,
        point=start_point_wcs,
    )
    start_point_ucs = ucs.from_wcs(start_point_wcs)
    end_point_ucs = ucs.from_wcs(end_point_wcs)
    def_point_ucs = Vec3(0, 0)

    arc = ConstructionArc.from_3p(start_point_ucs, end_point_ucs, def_point_ucs)
    dwg = ezdxf.new("R12")
    msp = dwg.modelspace()

    dxf_arc = arc.add_to_layout(msp, ucs)
    assert dxf_arc.dxftype() == "ARC"
    assert isclose(dxf_arc.dxf.radius, 0.81649658, abs_tol=1e-9)
    assert isclose(dxf_arc.dxf.start_angle, -30)
    assert isclose(dxf_arc.dxf.end_angle, -150)
    assert dxf_arc.dxf.extrusion.isclose(
        (0.57735027, 0.57735027, 0.57735027), abs_tol=1e-9
    )


def test_bounding_box():
    bbox = ConstructionArc(
        center=(0, 0), radius=1, start_angle=0, end_angle=90
    ).bounding_box
    assert bbox.extmin.isclose((0, 0))
    assert bbox.extmax.isclose((1, 1))

    bbox = ConstructionArc(
        center=(0, 0), radius=1, start_angle=0, end_angle=180
    ).bounding_box
    assert bbox.extmin.isclose((-1, 0))
    assert bbox.extmax.isclose((1, 1))

    bbox = ConstructionArc(
        center=(0, 0), radius=1, start_angle=270, end_angle=90
    ).bounding_box
    assert bbox.extmin.isclose((0, -1))
    assert bbox.extmax.isclose((1, 1))


def test_angles():
    arc = ConstructionArc(radius=1, start_angle=30, end_angle=60)
    assert tuple(arc.angles(2)) == (30, 60)
    assert tuple(arc.angles(3)) == (30, 45, 60)

    arc.start_angle = 180
    arc.end_angle = 0
    assert tuple(arc.angles(2)) == (180, 0)
    assert tuple(arc.angles(3)) == (180, 270, 0)

    arc.start_angle = -90
    arc.end_angle = -180
    assert tuple(arc.angles(2)) == (270, 180)
    assert tuple(arc.angles(4)) == (270, 0, 90, 180)


def test_vertices():
    angles = [0, 45, 90, 135, -45, -90, -135, 180]
    arc = ConstructionArc(center=(1, 1))
    vertices = list(arc.vertices(angles))
    for v, a in zip(vertices, angles):
        a = math.radians(a)
        assert v.isclose(Vec2((1 + math.cos(a), 1 + math.sin(a))))


def test_tangents():
    angles = [0, 45, 90, 135, -45, -90, -135, 180]
    sin45 = math.sin(math.pi / 4)
    result = [
        (0, 1),
        (-sin45, sin45),
        (-1, 0),
        (-sin45, -sin45),
        (sin45, sin45),
        (1, 0),
        (sin45, -sin45),
        (0, -1),
    ]
    arc = ConstructionArc(center=(1, 1))
    vertices = list(arc.tangents(angles))
    for v, r in zip(vertices, result):
        assert v.isclose(Vec2(r))


def test_angle_span():
    assert ConstructionArc(start_angle=30, end_angle=270).angle_span == 240
    # crossing 0-degree:
    assert (
        ConstructionArc(
            start_angle=30, end_angle=270, is_counter_clockwise=False
        ).angle_span
        == 120
    )
    # crossing 0-degree:
    assert ConstructionArc(start_angle=300, end_angle=60).angle_span == 120
    assert (
        ConstructionArc(
            start_angle=300, end_angle=60, is_counter_clockwise=False
        ).angle_span
        == 240
    )


def test_arc_segment_count():
    radius = 100
    max_sagitta = 2
    assert arc_segment_count(radius, math.tau, max_sagitta) == 16
    alpha = math.tau / 16
    l2 = math.sin(alpha / 2) * radius
    sagitta = radius - math.sqrt(radius**2 - l2**2)
    assert max_sagitta / 2 < sagitta < max_sagitta


class TestArcSegmentCountErrors:
    def test_radius_zero(self):
        assert arc_segment_count(radius=0, angle=math.tau, sagitta=1) == 1

    def test_sagitta_gt_radius(self):
        assert arc_segment_count(radius=1, angle=math.tau, sagitta=2) == 1


def test_arc_chord_length_domain_error():
    radius = 0.1
    assert arc_chord_length(radius, radius * 4) == 0.0


@pytest.mark.parametrize(
    "r, s, e, sagitta, count",
    [
        (1, 0, 180, 0.35, 3),
        (1, 0, 180, 0.10, 5),
        (0, 0, 360, 0.10, 0),  # radius 0 works but yields nothing
        (-1, 0, 180, 0.35, 3),  # negative radius same as positive radius
        (1, 270, 90, 0.10, 5),  # start angle > end angle
        (1, 90, -90, 0.10, 5),
        (1, 0, 0, 0.10, 0),  # angle span 0 works but yields nothing
        (1, -45, -45, 0.10, 0),
    ],
)
def test_flattening(r, s, e, sagitta, count):
    arc = ConstructionArc((0, 0), r, s, e)
    assert len(list(arc.flattening(sagitta))) == count


@pytest.mark.parametrize("p", [(2, 0), (2, 2), (0, 2), (2, -2), (0, -2)])
def test_point_is_in_arc_range(p):
    """
    Test if the angle defined by arc.center and point "p" is in the range
    arc.start_angle to arc.end_angle:
    """
    arc = ConstructionArc((0, 0), 1, -90, 90)
    assert arc._is_point_in_arc_range(Vec2(p)) is True


@pytest.mark.parametrize("p", [(-2, 0), (-2, 2), (-2, -2)])
def test_point_is_not_in_arc_range(p):
    """
    Test if the angle defined by arc.center and point "p" is NOT in the range
    arc.start_angle to arc.end_angle:
    """
    arc = ConstructionArc((0, 0), 1, -90, 90)
    assert arc._is_point_in_arc_range(Vec2(p)) is False


@pytest.mark.parametrize(
    "s, e",
    [
        [(0, 0), (2, 0)],  # touches the arc
        [(0, 0), (3, 0)],  # intersect
        [(0, 0), (0, 2)],  # touches the arc
        [(0, 0), (0, 3)],  # intersect
        [(0, 0), (2, 2)],  # intersect
        [(0, -1), (2, -1)],  # intersect
    ],
)
def test_arc_intersect_line_in_one_point(s, e):
    arc = ConstructionArc((0, 0), 2, -90, 90)
    assert len(arc.intersect_line(ConstructionLine(s, e))) == 1


@pytest.mark.parametrize(
    "s, e",
    [
        [(-2, 0), (2, 0)],  # touches
        [(-2, 1), (2, 1)],  # intersect
    ],
)
def test_arc_intersect_line_in_two_points(s, e):
    arc = ConstructionArc((0, 0), 2, 0, 180)
    assert len(arc.intersect_line(ConstructionLine(s, e))) == 2


@pytest.mark.parametrize(
    "s, e",
    [
        [(0, 2), (1, 2)],
        [(2, 0), (2, 1)],
        [(1, 1), (2, 2)],
    ],
)
def test_arc_does_not_intersect_line(s, e):
    arc = ConstructionArc((0, 0), 1, 0, 90)
    assert len(arc.intersect_line(ConstructionLine(s, e))) == 0


@pytest.mark.parametrize(
    "c, r",
    [
        [(0.0, 1.0), 1.0],
        [(0.0, 0.5), 0.5],
        [(2.0, 0.0), 1.0],
    ],
)
def test_arc_intersect_circle_in_one_point(c, r):
    arc = ConstructionArc((0, 0), 1, -90, 90)
    assert len(arc.intersect_circle(ConstructionCircle(c, r))) == 1


@pytest.mark.parametrize(
    "c, r",
    [
        [(1.0, 0.0), 1.0],
        [(0.5, 0.0), 1.0],
    ],
)
def test_arc_intersect_circle_in_two_points(c, r):
    arc = ConstructionArc((0, 0), 1, -90, 90)
    assert len(arc.intersect_circle(ConstructionCircle(c, r))) == 2


@pytest.mark.parametrize(
    "c, r",
    [
        [(0.0, 0.0), 0.5],  # concentric circle
        [(0.0, 0.0), 1.0],  # concentric circle
        [(0.0, 0.0), 2.0],  # concentric circle
        [(2.0, 0.0), 0.5],  # ) O
    ],
)
def test_arc_does_not_intersect_circle(c, r):
    arc = ConstructionArc((0, 0), 1, -90, 90)
    assert len(arc.intersect_circle(ConstructionCircle(c, r))) == 0


@pytest.mark.parametrize(
    "c, r, s, e",
    [
        [(2.0, 0.0), 1.0, 90, 270],  # touches in one point: )(
        [(1.5, 0.0), 1.0, 90, 180],  # intersect
    ],
)
def test_arc_intersect_arc_in_one_point(c, r, s, e):
    arc = ConstructionArc((0, 0), 1, -90, 90)
    assert len(arc.intersect_arc(ConstructionArc(c, r, s, e))) == 1


@pytest.mark.parametrize(
    "c, r, s, e",
    [
        [(0.5, 0.0), 1.0, 90, 270],  # intersect
        [(1.5, 0.0), 1.0, 90, 270],  # intersect
    ],
)
def test_arc_intersect_arc_in_two_points(c, r, s, e):
    arc = ConstructionArc((0, 0), 1, -90, 90)
    assert len(arc.intersect_arc(ConstructionArc(c, r, s, e))) == 2


@pytest.mark.parametrize(
    "c, r, s, e",
    [
        [(0.0, 0.0), 1.0, 90, 270],  # concentric arcs
        [(-0.5, 0.0), 1.0, 90, 270],  # insect circle but not arc: ( )
    ],
)
def test_arc_does_not_intersect_arc(c, r, s, e):
    arc = ConstructionArc((0, 0), 1, -90, 90)
    assert len(arc.intersect_arc(ConstructionArc(c, r, s, e))) == 0
