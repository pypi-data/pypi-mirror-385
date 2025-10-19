# Copyright (c) 2015-2021, Manfred Moitzi
# License: MIT License
import pytest
import math

import ezdxf
from ezdxf.entities import Hatch, BoundaryPathType, EdgeType
from ezdxf.lldxf.tagwriter import TagCollector, Tags
from ezdxf.lldxf import const
from ezdxf.math import Vec3


@pytest.fixture
def hatch():
    return Hatch.new()


@pytest.fixture
def path_hatch():
    return Hatch.from_text(PATH_HATCH)


@pytest.fixture
def edge_hatch():
    return Hatch.from_text(EDGE_HATCH)


@pytest.fixture
def spline_edge_hatch():
    return Hatch.from_text(EDGE_HATCH_WITH_SPLINE)


@pytest.fixture
def hatch_pattern():
    return Hatch.from_text(HATCH_PATTERN)


def test_default_settings(hatch):
    assert hatch.dxf.layer == "0"
    assert hatch.dxf.color == 256  # by layer
    assert hatch.dxf.linetype == "BYLAYER"
    assert hatch.dxf.ltscale == 1.0
    assert hatch.dxf.invisible == 0
    assert hatch.dxf.extrusion == (0.0, 0.0, 1.0)
    assert hatch.dxf.elevation == (0.0, 0.0, 0.0)


def test_default_hatch_settings(hatch):
    assert hatch.has_solid_fill is True
    assert hatch.has_gradient_data is False
    assert hatch.has_pattern_fill is False

    assert hatch.dxf.solid_fill == 1
    assert hatch.dxf.hatch_style == 0
    assert hatch.dxf.pattern_type == 1
    assert hatch.dxf.pattern_angle == 0
    assert hatch.dxf.pattern_scale == 1
    assert hatch.dxf.pattern_double == 0
    assert hatch.dxf.n_seed_points == 0


def test_get_seed_points(hatch):
    assert len(hatch.seeds) == 0


def test_set_seed_points(hatch):
    seed_points = [(1.0, 1.0), (2.0, 2.0)]
    hatch.set_seed_points(seed_points)
    assert 2 == hatch.dxf.n_seed_points
    assert seed_points == hatch.seeds


def test_remove_all_paths(path_hatch):
    path_hatch.paths.clear()
    assert 0 == len(path_hatch.paths), "invalid boundary path count"


def test_polyline_path_attribs(path_hatch):
    path = path_hatch.paths[0]  # test first boundary path
    assert path.type == BoundaryPathType.POLYLINE
    assert 4 == len(path.vertices)
    assert path.has_bulge() is False
    assert path.is_closed == 1
    assert 7 == path.path_type_flags, "unexpected path type flags"


def test_polyline_path_vertices(path_hatch):
    path = path_hatch.paths[0]  # test first boundary path
    assert path.type == BoundaryPathType.POLYLINE
    assert 4 == len(path.vertices)
    # vertex format: x, y, bulge_value
    assert (10, 10, 0) == path.vertices[0], "invalid first vertex"
    assert (10, 0, 0) == path.vertices[3], "invalid last vertex"


def test_edge_path_count(edge_hatch):
    assert len(edge_hatch.paths) == 1, "invalid boundary path count"


def test_edge_path_type(edge_hatch):
    path = edge_hatch.paths[0]
    assert path.type == BoundaryPathType.EDGE


def test_edge_path_edges(edge_hatch):
    path = edge_hatch.paths[0]
    edge = path.edges[0]
    assert edge.type == EdgeType.ELLIPSE, "expected ellipse edge as 1. edge"
    assert (10, 5) == edge.center
    assert (3, 0) == edge.major_axis
    assert 1.0 / 3.0 == edge.ratio
    assert 270 == edge.start_angle
    assert 450 == edge.end_angle  # this value was created by AutoCAD == 90 degree
    assert 1 == edge.ccw

    edge = path.edges[1]
    assert edge.type == EdgeType.LINE, "expected line edge type as 2. edge"
    assert (10, 6) == edge.start
    assert (10, 10) == edge.end

    edge = path.edges[2]
    assert edge.type == EdgeType.LINE, "expected line edge as 3. edge"
    assert (10, 10) == edge.start
    assert (6, 10) == edge.end

    edge = path.edges[3]
    assert edge.type == EdgeType.ARC, "expected arc edge as 4. edge"
    assert (5, 10) == edge.center
    assert 1 == edge.radius
    # clockwise arc edge:
    assert 0 == edge.ccw
    # now we get converted and swapped angles
    assert 360 == 360.0 - edge.end_angle  # this value was created by AutoCAD (0 degree)
    assert (
        540 == 360.0 - edge.start_angle
    )  # this value was created by AutoCAD (-180 degree)
    assert -180 == edge.start_angle  # ezdxf representation
    assert 0 == edge.end_angle  # ezdxf representation

    edge = path.edges[4]
    assert edge.type == EdgeType.LINE, "expected line edge as 5. edge"
    assert (4, 10) == edge.start
    assert (0, 10) == edge.end

    edge = path.edges[5]
    assert edge.type == EdgeType.LINE, "expected line edge as 6. edge"
    assert (0, 10) == edge.start
    assert (0, 0) == edge.end

    edge = path.edges[6]
    assert edge.type == EdgeType.LINE, "expected line edge as 7. edge"
    assert (0, 0) == edge.start
    assert (10, 0) == edge.end

    edge = path.edges[7]
    assert edge.type == EdgeType.LINE, "expected line edge as 8. edge"
    assert (10, 0) == edge.start
    assert (10, 4) == edge.end


def test_spline_edge_hatch_get_params(spline_edge_hatch):
    path = spline_edge_hatch.paths[0]
    spline = None
    for edge in path.edges:
        if edge.type == EdgeType.SPLINE:
            spline = edge
            break
    assert spline is not None, "Spline edge not found."
    assert 3 == spline.degree
    assert 0 == spline.rational
    assert 0 == spline.periodic
    assert (0, 0) == spline.start_tangent
    assert (0, 0) == spline.end_tangent
    assert 10 == len(spline.knot_values)
    assert 11.86874452602773 == spline.knot_values[-1]
    assert 6 == len(spline.control_points)
    assert (0, 10) == spline.control_points[0], "Unexpected start control point."
    assert (0, 0) == spline.control_points[-1], "Unexpected end control point."
    assert 0 == len(spline.weights)
    assert 4 == len(spline.fit_points)
    assert (0, 10) == spline.fit_points[0], "Unexpected start fit point."
    assert (0, 0) == spline.fit_points[-1], "Unexpected end fit point."


def test_create_spline_edge(spline_edge_hatch):
    # create the spline
    path = spline_edge_hatch.paths[0]
    spline = path.add_spline([(1, 1), (2, 2), (3, 3), (4, 4)], degree=3, periodic=1)
    # the following values do not represent a mathematically valid spline
    spline.control_points = [(1, 1), (2, 2), (3, 3), (4, 4)]
    spline.knot_values = [1, 2, 3, 4, 5, 6]
    spline.weights = [4, 3, 2, 1]
    spline.start_tangent = (10, 1)
    spline.end_tangent = (2, 20)

    # test the spline
    path = spline_edge_hatch.paths[0]
    spline = path.edges[-1]
    assert 3 == spline.degree
    assert 1 == spline.periodic
    assert (10, 1) == spline.start_tangent
    assert (2, 20) == spline.end_tangent
    assert [(1, 1), (2, 2), (3, 3), (4, 4)] == spline.control_points
    assert [(1, 1), (2, 2), (3, 3), (4, 4)] == spline.fit_points
    assert [1, 2, 3, 4, 5, 6] == spline.knot_values
    assert [4, 3, 2, 1] == spline.weights

    writer = TagCollector()
    spline.export_dxf(writer)
    tags = Tags(writer.tags)
    assert tags.get_first_value(97) == 4, "expected count of fit points"


def test_create_required_tangents_for_spline_edge_if_fit_points_present(
    spline_edge_hatch,
):
    # create the spline
    path = spline_edge_hatch.paths[0]
    spline = path.add_spline_control_frame(fit_points=[(1, 1), (2, 2), (3, 3), (4, 4)])
    writer = TagCollector()
    spline.export_dxf(writer)
    tags = Tags(writer.tags)
    assert tags.get_first_value(97) == 4, "expected count of fit points"
    assert tags.has_tag(12), "expected start tangent to be present"
    assert tags.has_tag(13), "expected end tangent to be present"


def test_no_fit_points_export(spline_edge_hatch):
    path = spline_edge_hatch.paths[0]
    spline = path.add_spline(
        control_points=[(1, 1), (2, 2), (3, 3), (4, 4)], degree=3, periodic=1
    )
    spline.knot_values = [1, 2, 3, 4, 5, 6]
    assert [(1, 1), (2, 2), (3, 3), (4, 4)] == spline.control_points
    assert len(spline.fit_points) == 0
    writer = TagCollector(dxfversion=const.DXF2007)
    spline.export_dxf(writer)
    # do not write length tag 97 if no fit points exists for DXF2007 and prior
    assert any(tag.code == 97 for tag in writer.tags) is False

    writer = TagCollector(dxfversion=const.DXF2010)
    spline.export_dxf(writer)
    # do write length tag 97 if no fit points exists for DXF2010+
    assert (97, 0) in writer.tags


def test_is_pattern_hatch(hatch_pattern):
    assert hatch_pattern.has_solid_fill is False
    assert hatch_pattern.has_gradient_data is False
    assert hatch_pattern.has_pattern_fill is True


def test_edit_pattern(hatch_pattern):
    pattern = hatch_pattern.pattern
    assert 2 == len(pattern.lines)

    line0 = pattern.lines[0]
    assert 45 == line0.angle
    assert (0, 0) == line0.base_point
    assert (-0.1767766952966369, 0.1767766952966369) == line0.offset
    assert 0 == len(line0.dash_length_items)

    line1 = pattern.lines[1]
    assert 45 == line1.angle
    assert (0.176776695, 0) == line1.base_point
    assert (-0.1767766952966369, 0.1767766952966369) == line1.offset
    assert 2 == len(line1.dash_length_items)
    assert [0.125, -0.0625] == line1.dash_length_items


@pytest.fixture()
def pattern():
    return [
        [45, (0, 0), (0, 1), []],  # 1. Line: continuous
        [45, (0, 0.5), (0, 1), [0.2, -0.1]],  # 2. Line: dashed
    ]


def test_create_new_pattern_hatch(hatch, pattern):
    hatch.set_pattern_fill("MOZMAN", definition=pattern)
    assert hatch.has_solid_fill is False
    assert hatch.has_gradient_data is False
    assert hatch.has_pattern_fill is True

    assert "MOZMAN" == hatch.dxf.pattern_name

    line0 = hatch.pattern.lines[0]
    assert 45 == line0.angle
    assert (0, 0) == line0.base_point
    assert (0, 1) == line0.offset
    assert 0 == len(line0.dash_length_items)

    line1 = hatch.pattern.lines[1]
    assert 45 == line1.angle
    assert (0, 0.5) == line1.base_point
    assert (0, 1) == line1.offset
    assert 2 == len(line1.dash_length_items)
    assert [0.2, -0.1] == line1.dash_length_items


def test_pattern_scale(hatch, pattern):
    hatch.set_pattern_fill("MOZMAN", definition=pattern)
    hatch.set_pattern_scale(2)
    assert hatch.dxf.pattern_scale == 2
    line1, line2 = hatch.pattern.lines
    assert line1.base_point == (0, 0)
    assert line1.offset == (0, 2)
    assert line2.base_point == (0, 1)
    assert line2.offset == (0, 2)


def test_pattern_scale_x_times(hatch, pattern):
    hatch.set_pattern_fill("MOZMAN", definition=pattern)
    hatch.set_pattern_scale(2)
    # scale pattern 3 times of actual scaling 2
    # = base pattern x 6
    hatch.set_pattern_scale(hatch.dxf.pattern_scale * 3)
    assert hatch.dxf.pattern_scale == 6
    line1, line2 = hatch.pattern.lines
    assert line1.base_point == (0, 0)
    assert line1.offset == (0, 6)
    assert line2.base_point == (0, 3)
    assert line2.offset == (0, 6)


def test_pattern_rotation(hatch, pattern):
    hatch.set_pattern_fill("MOZMAN", definition=pattern)
    assert hatch.dxf.pattern_angle == 0
    hatch.set_pattern_angle(45)
    assert hatch.dxf.pattern_angle == 45
    line1, line2 = hatch.pattern.lines
    assert line1.angle == 90
    assert line1.base_point == (0, 0)
    assert line1.offset.isclose(Vec3(-0.7071067811865475, 0.7071067811865476))
    assert line2.angle == 90
    assert line2.base_point.isclose(Vec3(-0.35355339059327373, 0.3535533905932738))
    assert line2.offset.isclose(Vec3(-0.7071067811865475, 0.7071067811865476))


def test_pattern_rotation_add_angle(hatch, pattern):
    hatch.set_pattern_fill("MOZMAN", definition=pattern)
    assert hatch.dxf.pattern_angle == 0
    hatch.set_pattern_angle(45)
    assert hatch.dxf.pattern_angle == 45

    # add 45 degrees to actual pattern rotation
    hatch.set_pattern_angle(hatch.dxf.pattern_angle + 45)
    assert hatch.dxf.pattern_angle == 90


def test_create_gradient(hatch):
    hatch.set_gradient((10, 10, 10), (250, 250, 250), rotation=180.0)
    assert hatch.has_gradient_data is True
    assert hatch.has_solid_fill is True
    assert hatch.has_pattern_fill is False

    gdata = hatch.gradient
    assert (10, 10, 10) == gdata.color1
    assert (250, 250, 250) == gdata.color2
    assert 180 == int(gdata.rotation)
    assert 0 == gdata.centered
    assert 0 == gdata.tint
    assert "LINEAR" == gdata.name


def test_create_gradient_low_level_dxf_tags(hatch):
    hatch.set_gradient((10, 10, 10), (250, 250, 250), rotation=180.0)
    tags = TagCollector.dxftags(hatch.gradient)
    for code in [450, 451, 452, 453, 460, 461, 462, 470]:
        assert tags.has_tag(code) is True, "missing required tag: %d" % code
    assert 2 == len(tags.find_all(463))
    assert 2 == len(tags.find_all(421))


def test_remove_gradient_data(hatch):
    hatch.set_gradient((10, 10, 10), (250, 250, 250), rotation=180.0)
    assert hatch.has_gradient_data is True

    hatch.set_solid_fill(color=4)  # remove gradient data
    assert hatch.has_gradient_data is False, "gradient data not removed"
    assert hatch.has_pattern_fill is False
    assert hatch.has_solid_fill is True


def test_remove_gradient_low_level_dxf_tags(hatch):
    hatch.set_gradient((10, 10, 10), (250, 250, 250), rotation=180.0)
    assert hatch.has_gradient_data is True

    hatch.set_solid_fill(color=4)  # remove gradient data
    assert hatch.gradient is None


def test_bgcolor_not_exists(hatch):
    assert hatch.bgcolor is None


def test_set_new_bgcolor(hatch):
    hatch.bgcolor = (10, 20, 30)
    assert (10, 20, 30) == hatch.bgcolor


def test_change_bgcolor(hatch):
    hatch.bgcolor = (10, 20, 30)
    assert (10, 20, 30) == hatch.bgcolor
    hatch.bgcolor = (30, 20, 10)
    assert (30, 20, 10) == hatch.bgcolor


def test_delete_bgcolor(hatch):
    hatch.bgcolor = (10, 20, 30)
    assert (10, 20, 30) == hatch.bgcolor
    del hatch.bgcolor
    assert hatch.bgcolor is None


def test_delete_not_existing_bgcolor(hatch):
    del hatch.bgcolor
    assert hatch.bgcolor is None


@pytest.fixture(scope="module")
def msp():
    doc = ezdxf.new()
    return doc.modelspace()


VERTICES = [(0, 0), (1, 0), (1, 1), (0, 1)]


def add_hatch(msp):
    hatch = msp.add_hatch()
    path = hatch.paths.add_polyline_path(VERTICES)
    return hatch, path


def test_associate_valid_entity(msp):
    hatch, path = add_hatch(msp)
    pline = msp.add_lwpolyline(VERTICES, close=True)
    hatch.associate(path, [pline])
    assert path.source_boundary_objects == [pline.dxf.handle]


def test_if_hatch_is_alive_before_association(msp):
    hatch, path = add_hatch(msp)
    hatch.destroy()
    with pytest.raises(const.DXFStructureError):
        hatch.associate(path, [])


def test_can_not_associate_entity_from_different_document(msp):
    hatch, path = add_hatch(msp)
    pline = msp.add_lwpolyline(VERTICES, close=True)
    pline.doc = None
    with pytest.raises(const.DXFStructureError):
        hatch.associate(path, [pline])


def test_can_not_associate_entity_with_different_owner(msp):
    hatch, path = add_hatch(msp)
    pline = msp.add_lwpolyline(VERTICES, close=True)
    pline.dxf.owner = None
    with pytest.raises(const.DXFStructureError):
        hatch.associate(path, [pline])


def test_can_not_associate_destroyed_entity(msp):
    hatch, path = add_hatch(msp)
    pline = msp.add_lwpolyline(VERTICES, close=True)
    pline.destroy()
    with pytest.raises(const.DXFStructureError):
        hatch.associate(path, [pline])


@pytest.fixture
def square_hatch():
    hatch = Hatch()
    hatch.paths.add_polyline_path([(0, 0), (10, 0), (10, 10), (0, 10)])
    return hatch


def test_triangulate_hatch(square_hatch: Hatch):
    square_hatch.set_solid_fill(3)
    triangles = list(square_hatch.triangulate(0.01))
    assert len(triangles) == 2
    assert (
        len(list(square_hatch.render_pattern_lines())) == 0
    ), "pattern rendering not supported"


def test_triangulate_with_elevation(square_hatch: Hatch):
    square_hatch.dxf.elevation = Vec3(0, 0, 10)
    square_hatch.set_solid_fill(3)
    triangles = list(square_hatch.triangulate(0.01))
    assert all([math.isclose(v.z, 10) for v in t] for t in triangles) is True


def test_render_pattern_lines(square_hatch: Hatch):
    square_hatch.set_pattern_fill("ANSI31", scale=0.5)
    lines = list(square_hatch.render_pattern_lines())
    assert len(lines) > 8
    assert (
        len(list(square_hatch.triangulate(0.01))) == 2
    ), "expected triangulation support"


def test_render_pattern_lines_with_elevation(square_hatch: Hatch):
    square_hatch.set_pattern_fill("ANSI31", scale=0.5)
    square_hatch.dxf.elevation = Vec3(0, 0, 10)
    lines = list(square_hatch.render_pattern_lines())
    assert all([math.isclose(v.z, 10) for v in line] for line in lines) is True


PATH_HATCH = """  0
HATCH
  5
27C
330
1F
100
AcDbEntity
  8
0
 62
     1
100
AcDbHatch
 10
0.0
 20
0.0
 30
0.0
210
0.0
220
0.0
230
1.0
  2
SOLID
 70
     1
 71
     0
 91
        1
 92
        7
 72
     0
 73
     1
 93
        4
 10
10.0
 20
10.0
 10
0.0
 20
10.0
 10
0.0
 20
0.0
 10
10.0
 20
0.0
 97
        0
 75
     1
 76
     1
 47
0.0442352806926743
 98
        1
 10
4.826903383179796
 20
4.715694827530256
450
        0
451
        0
460
0.0
461
0.0
452
        0
462
1.0
453
        2
463
0.0
 63
     5
421
      255
463
1.0
 63
     2
421
 16776960
470
LINEAR
1001
GradientColor1ACI
1070
     5
1001
GradientColor2ACI
1070
     2
1001
ACAD
1010
0.0
1020
0.0
1030
0.0
"""

EDGE_HATCH = """  0
HATCH
  5
1FE
330
1F
100
AcDbEntity
  8
0
100
AcDbHatch
 10
0.0
 20
0.0
 30
0.0
210
0.0
220
0.0
230
1.0
  2
SOLID
 70
     1
 71
     1
 91
        1
 92
        5
 93
        8
 72
     3
 10
10.0
 20
5.0
 11
3.0
 21
0.0
 40
0.3333333333333333
 50
270
 51
450
 73
     1
 72
     1
 10
10.0
 20
6.0
 11
10.0
 21
10.0
 72
     1
 10
10.0
 20
10.0
 11
6.0
 21
10.0
 72
     2
 10
5.0
 20
10.0
 40
1.0
 50
360.0
 51
540.0
 73
     0
 72
     1
 10
4.0
 20
10.0
 11
0.0
 21
10.0
 72
     1
 10
0.0
 20
10.0
 11
0.0
 21
0.0
 72
     1
 10
0.0
 20
0.0
 11
10.0
 21
0.0
 72
     1
 10
10.0
 20
0.0
 11
10.0
 21
4.0
 97
        8
330
1E7
330
1EC
330
1E4
330
1E6
330
1EA
330
1E5
330
1E2
330
1E3
 75
     1
 76
     1
 47
0.0226465124087611
 98
        1
 10
5.15694040451099
 20
5.079032000141936
450
        0
451
        0
460
0.0
461
0.0
452
        0
462
1.0
453
        2
463
0.0
 63
     5
421
      255
463
1.0
 63
     2
421
 16776960
470
LINEAR
1001
GradientColor1ACI
1070
     5
1001
GradientColor2ACI
1070
     2
1001
ACAD
1010
0.0
1020
0.0
1030
0.0
"""

EDGE_HATCH_WITH_SPLINE = """  0
HATCH
  5
220
330
1F
100
AcDbEntity
  8
0
 62
     1
100
AcDbHatch
 10
0.0
 20
0.0
 30
0.0
210
0.0
220
0.0
230
1.0
  2
SOLID
 70
     1
 71
     1
 91
        1
 92
        5
 93
        4
 72
     1
 10
10.0
 20
10.0
 11
0.0
 21
10.0
 72
     4
 94
        3
 73
     0
 74
     0
 95
       10
 96
        6
 40
0.0
 40
0.0
 40
0.0
 40
0.0
 40
3.354101966249684
 40
7.596742653368969
 40
11.86874452602773
 40
11.86874452602773
 40
11.86874452602773
 40
11.86874452602773
 10
0.0
 20
10.0
 10
0.8761452790665735
 20
8.935160214313272
 10
2.860536415354832
 20
6.523392802252294
 10
-3.08307347911064
 20
4.314363374126372
 10
-1.030050983735315
 20
1.441423393837641
 10
0.0
 20
0.0
 97
        4
 11
0.0
 21
10.0
 11
1.5
 21
7.0
 11
-1.5
 21
4.0
 11
0.0
 21
0.0
 12
0.0
 22
0.0
 13
0.0
 23
0.0
 72
     1
 10
0.0
 20
0.0
 11
10.0
 21
0.0
 72
     1
 10
10.0
 20
0.0
 11
10.0
 21
10.0
 97
        4
330
215
330
217
330
213
330
214
 75
     1
 76
     1
 47
0.0365335049696054
 98
        1
 10
5.5
 20
4.5
450
        0
451
        0
460
0.0
461
0.0
452
        0
462
1.0
453
        2
463
0.0
 63
     5
421
      255
463
1.0
 63
     2
421
 16776960
470
LINEAR
1001
GradientColor1ACI
1070
     5
1001
GradientColor2ACI
1070
     2
1001
ACAD
1010
0.0
1020
0.0
1030
0.0
"""

HATCH_PATTERN = """0
HATCH
  5
1EA
330
1F
100
AcDbEntity
  8
0
100
AcDbHatch
 10
0.0
 20
0.0
 30
0.0
210
0.0
220
0.0
230
1.0
  2
ANSI33
 70
     0
 71
     0
 91
        1
 92
        7
 72
     0
 73
     1
 93
        4
 10
10.0
 20
10.0
 10
0.0
 20
10.0
 10
0.0
 20
0.0
 10
10.0
 20
0.0
 97
        0
 75
     1
 76
     1
 52
0.0
 41
1.0
 77
     0
 78
     2
 53
45.0
 43
0.0
 44
0.0
 45
-0.1767766952966369
 46
0.1767766952966369
 79
     0
 53
45.0
 43
0.176776695
 44
0.0
 45
-0.1767766952966369
 46
0.1767766952966369
 79
     2
 49
0.125
 49
-0.0625
 47
0.0180224512632811
 98
        1
 10
3.5
 20
6.0
1001
GradientColor1ACI
1070
     5
1001
GradientColor2ACI
1070
     2
1001
ACAD
1010
0.0
1020
0.0
1030
0.0
"""
