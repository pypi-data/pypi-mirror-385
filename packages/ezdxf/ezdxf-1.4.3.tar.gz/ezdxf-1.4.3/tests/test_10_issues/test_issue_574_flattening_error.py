#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest

from ezdxf.entities import LWPolyline, Ellipse
from ezdxf import path


@pytest.fixture
def lwpolyline1():
    e = LWPolyline.new(
        dxfattribs={
            "layer": "0",
            "linetype": "Continuous",
            "color": 0,
            "flags": 0,
            "const_width": 0.0,
            "elevation": 2.999999999999999e99,
            "extrusion": (0.0, 0.0, 1.0),
        },
    )
    e.set_points(
        [
            (297888, 108770, 0.0, 0.0, 0.0512534542487669),
            (297930, 108335, 0.0, 0.0, 0.0),
        ]
    )
    return e


MAX_SAGITTA = 0.01


def test_flattening_by_arc(lwpolyline1: LWPolyline):
    entities = list(lwpolyline1.virtual_entities())
    for e in entities:
        if e.dxftype() == "ARC":
            points = list(e.flattening(MAX_SAGITTA))
            assert len(points) > 0

            ellipse = Ellipse.from_arc(e)
            points = list(ellipse.flattening(0.01))
            assert len(points) > 0


def test_flattening_by_ellipse(lwpolyline1: LWPolyline):
    entities = list(lwpolyline1.virtual_entities())
    for e in entities:
        if e.dxftype() == "ARC":
            ellipse = Ellipse.from_arc(e)
            points = list(ellipse.flattening(MAX_SAGITTA))
            assert len(points) > 0


def test_flattening_by_path(lwpolyline1):
    p = path.make_path(lwpolyline1)
    points = list(p.flattening(distance=MAX_SAGITTA))
    assert len(points) > 0


@pytest.fixture
def ellipse1():
    return Ellipse.new(
        dxfattribs={
            "center": (
                298998.9237372455,
                105908.98587737791,
                0.0218015606544459,
            ),
            "major_axis": (-2.005925505480262, 9.590684825374422e-13, 0.0),
            "ratio": 0.6052078628034204,
            "start_param": 7.898e-13,
            "end_param": 7.878142582740111e-13,
            "extrusion": (0.0, -0.0, 1.0),
        },
    )


def test_flattening_ellipse(ellipse1: Ellipse):
    points = list(ellipse1.flattening(MAX_SAGITTA))
    assert len(points) > 0


if __name__ == "__main__":
    pytest.main([__file__])
