#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
import pytest
from ezdxf.entities import Hatch
from ezdxf.math import Vec2


@pytest.fixture
def all_edge_types_hatch():
    # used in test files:
    # 229c
    # 250
    hatch = Hatch.new(
        dxfattribs={
            "layer": "0",
            "color": "2",
            "elevation": (0.0, 0.0, 0.0),
            "extrusion": (0.0, 0.0, 1.0),
            "pattern_name": "SOLID",
            "solid_fill": 1,
            "associative": 0,
            "hatch_style": 0,
            "pattern_type": 1,
        },
    )
    # edge-path contains all supported edge types:
    ep = hatch.paths.add_edge_path(flags=1)
    ep.add_arc(  # clockwise oriented ARC
        center=(0.0, 13.0),
        radius=3.0,
        start_angle=-90.0,
        end_angle=90.0,
        ccw=False,
    )
    ep.add_ellipse(  # clockwise oriented ELLIPSE
        center=(0.0, 5.0),
        major_axis=(0.0, 5.0),
        ratio=0.6,
        start_angle=180.0,
        end_angle=360.0,
        ccw=False,
    )
    ep.add_line((0.0, 0.0), (10.0, 0.0))  # LINE
    ep.add_ellipse(  # counter-clockwise oriented ELLIPSE
        center=(10.0, 5.0),
        major_axis=(0.0, -5.0),
        ratio=0.6,
        start_angle=0.0,
        end_angle=180.0,
        ccw=True,
    )
    ep.add_arc(  # counter-clockwise oriented ARC
        center=(10.0, 13.0),
        radius=3.0,
        start_angle=270.0,
        end_angle=450.0,
        ccw=True,
    )
    ep.add_spline(  # SPLINE
        control_points=[
            Vec2(10.0, 16.0),
            Vec2(9.028174684192452, 16.0),
            Vec2(6.824943218065775, 12.14285714285714),
            Vec2(3.175056781934232, 19.85714285714287),
            Vec2(0.9718253158075516, 16.0),
            Vec2(0, 16.0),
        ],
        knot_values=[
            0.0,
            0.0,
            0.0,
            0.0,
            2.91547594742265,
            8.746427842267952,
            11.6619037896906,
            11.6619037896906,
            11.6619037896906,
            11.6619037896906,
        ],
        degree=3,
        periodic=0,
    )
    return hatch
