import datetime as dt

import pytest
from pydantic import ValidationError

from czml3.enums import (
    ArcTypes,
    ClassificationTypes,
    ColorBlendModes,
    CornerTypes,
    HeightReferences,
    ShadowModes,
)
from czml3.properties import (
    ArcType,
    Billboard,
    Box,
    BoxDimensions,
    CheckerboardMaterial,
    ClassificationType,
    Clock,
    Color,
    ColorBlendMode,
    CornerType,
    DistanceDisplayCondition,
    Ellipsoid,
    EllipsoidRadii,
    EyeOffset,
    GridMaterial,
    HeightReference,
    ImageMaterial,
    Label,
    Material,
    Model,
    NearFarScalar,
    Orientation,
    Point,
    Polygon,
    Polyline,
    PolylineArrowMaterial,
    PolylineDashMaterial,
    PolylineGlowMaterial,
    PolylineMaterial,
    PolylineOutlineMaterial,
    Position,
    PositionList,
    PositionListOfLists,
    RectangleCoordinates,
    ShadowMode,
    SolidColorMaterial,
    StripeMaterial,
    Tileset,
    Uri,
    ViewFrom,
)
from czml3.types import (
    Cartesian2Value,
    Cartesian3ListOfListsValue,
    Cartesian3ListValue,
    Cartesian3Value,
    Cartesian3VelocityValue,
    CartographicDegreesListOfListsValue,
    CartographicDegreesListValue,
    CartographicDegreesValue,
    CartographicRadiansListOfListsValue,
    CartographicRadiansListValue,
    CartographicRadiansValue,
    DistanceDisplayConditionValue,
    IntervalValue,
    NearFarScalarValue,
    ReferenceListOfListsValue,
    ReferenceListValue,
    ReferenceValue,
    TimeInterval,
    TimeIntervalCollection,
    UnitQuaternionValue,
    format_datetime_like,
)


def test_box():
    expected_result = """{
    "show": true,
    "dimensions": {
        "cartesian": [
            5.0,
            6.0,
            3.0
        ]
    }
}"""

    box = Box(
        show=True, dimensions=BoxDimensions(cartesian=Cartesian3Value(values=[5, 6, 3]))
    )
    assert str(box) == expected_result


def test_eyeOffset():
    expected_result = """{
    "cartesian": [
        1.0,
        2.0,
        3.0
    ]
}"""

    eyeOffset = EyeOffset(cartesian=Cartesian3Value(values=[1, 2, 3]))
    assert str(eyeOffset) == expected_result


def test_clock():
    expected_result = """{
    "interval": "2019-06-11T12:26:58.000000Z/2019-06-11T12:26:58.000000Z"
}"""
    clock = Clock(
        interval=TimeInterval(
            start="2019-06-11T12:26:58.000000Z",
            end="2019-06-11T12:26:58.000000Z",
        )
    )

    assert str(clock) == expected_result


def test_point():
    expected_result = """{
    "show": true,
    "pixelSize": 10.0,
    "scaleByDistance": {
        "nearFarScalar": [
            150.0,
            2.0,
            15000000.0,
            0.5
        ]
    },
    "disableDepthTestDistance": 1.2
}"""

    pnt = Point(
        show=True,
        pixelSize=10,
        scaleByDistance=NearFarScalar(
            nearFarScalar=NearFarScalarValue(values=[150, 2.0, 15000000, 0.5])
        ),
        disableDepthTestDistance=1.2,
    )
    assert str(pnt) == expected_result


def test_NearFarScalar_list():
    expected_result = """{
    "show": true,
    "pixelSize": 10.0,
    "scaleByDistance": {
        "nearFarScalar": [
            150.0,
            2.0,
            15000000.0,
            0.5
        ]
    },
    "disableDepthTestDistance": 1.2
}"""

    pnt = Point(
        show=True,
        pixelSize=10,
        scaleByDistance=NearFarScalar(nearFarScalar=[150, 2.0, 15000000, 0.5]),
        disableDepthTestDistance=1.2,
    )
    assert str(pnt) == expected_result


def test_arc_type():
    expected_result = """{
    "arcType": "NONE"
}"""
    arc_type = ArcType(arcType=ArcTypes.NONE)
    assert str(arc_type) == expected_result


def test_shadow_mode():
    expected_result = """{
    "shadowMode": "ENABLED"
}"""
    shadow_mode = ShadowMode(shadowMode=ShadowModes.ENABLED)
    assert str(shadow_mode) == expected_result


def test_polyline():
    expected_result = """{
    "positions": {
        "cartographicDegrees": [
            20.0,
            30.0,
            10.0
        ]
    },
    "arcType": {
        "arcType": "GEODESIC"
    },
    "distanceDisplayCondition": {
        "distanceDisplayCondition": [
            14.0,
            81.0
        ]
    },
    "classificationType": {
        "classificationType": "CESIUM_3D_TILE"
    }
}"""
    pol = Polyline(
        positions=PositionList(
            cartographicDegrees=CartographicDegreesListValue(values=[20, 30, 10])
        ),
        arcType=ArcType(arcType="GEODESIC"),
        distanceDisplayCondition=DistanceDisplayCondition(
            distanceDisplayCondition=DistanceDisplayConditionValue(values=[14, 81])
        ),
        classificationType=ClassificationType(
            classificationType=ClassificationTypes.CESIUM_3D_TILE
        ),
    )
    assert str(pol) == expected_result


def test_material_solid_color():
    expected_result = """{
    "solidColor": {
        "color": {
            "rgba": [
                200.0,
                100.0,
                30.0,
                255.0
            ]
        }
    }
}"""
    mat = Material(solidColor=SolidColorMaterial(color=Color(rgba=[200, 100, 30])))

    assert str(mat) == expected_result

    pol_mat = PolylineMaterial(
        solidColor=SolidColorMaterial(color=Color(rgba=[200, 100, 30]))
    )
    assert str(pol_mat) == expected_result


def test_arrowmaterial_color():
    expected_result = """{
    "polylineArrow": {
        "color": {
            "rgba": [
                200.0,
                100.0,
                30.0,
                255.0
            ]
        }
    }
}"""
    pamat = PolylineMaterial(
        polylineArrow=PolylineArrowMaterial(color=Color(rgba=[200, 100, 30, 255])),
    )

    assert str(pamat) == expected_result


def test_dashmaterial_colors():
    expected_result = """{
    "polylineDash": {
        "color": {
            "rgba": [
                200.0,
                100.0,
                30.0,
                255.0
            ]
        },
        "gapColor": {
            "rgba": [
                100.0,
                200.0,
                0.0,
                255.0
            ]
        },
        "dashLength": 16.0,
        "dashPattern": 255
    }
}"""
    dashmat = PolylineMaterial(
        polylineDash=PolylineDashMaterial(
            color=Color(rgba=[200, 100, 30, 255]),
            gapColor=Color(rgba=[100, 200, 0, 255]),
            dashLength=16,
            dashPattern=255,
        ),
    )

    assert str(dashmat) == expected_result


def test_glowmaterial_color():
    expected_result = """{
    "polylineGlow": {
        "color": {
            "rgba": [
                200.0,
                100.0,
                30.0,
                255.0
            ]
        },
        "glowPower": 0.7,
        "taperPower": 0.3
    }
}"""
    glowmat = PolylineMaterial(
        polylineGlow=PolylineGlowMaterial(
            color=Color(rgba=[200, 100, 30, 255]), glowPower=0.7, taperPower=0.3
        )
    )
    assert str(glowmat) == expected_result


def test_outline_material_colors():
    expected_result = """{
    "polylineOutline": {
        "color": {
            "rgba": [
                200.0,
                100.0,
                30.0,
                255.0
            ]
        },
        "outlineColor": {
            "rgba": [
                100.0,
                200.0,
                0.0,
                255.0
            ]
        },
        "outlineWidth": 3.0
    }
}"""
    omat = PolylineMaterial(
        polylineOutline=PolylineOutlineMaterial(
            color=Color(rgba=[200, 100, 30, 255]),
            outlineColor=Color(rgba=[100, 200, 0, 255]),
            outlineWidth=3,
        )
    )
    assert str(omat) == expected_result


def test_positionlist_epoch():
    expected_result = """{
    "cartographicDegrees": [
        200.0,
        100.0,
        30.0
    ],
    "epoch": "2019-06-11T12:26:58.000000Z"
}"""
    p = PositionList(
        epoch=dt.datetime(2019, 6, 11, 12, 26, 58, tzinfo=dt.timezone.utc),
        cartographicDegrees=[200, 100, 30],
    )
    assert str(p) == expected_result


def test_colors_rgba():
    Color(rgba=[255, 204, 0, 55])
    Color(rgba=[255, 204, 55])
    Color(rgba=[0.5, 0.6, 0.2])
    Color(rgba="0xFF0000")
    Color(rgba="0xFFFFFFFF")
    Color(rgba="0xFF3223")
    Color(rgba="0xFF322332")
    Color(rgba="#FF3223")
    Color(rgba="#FF322332")
    Color(rgba=[255, 204, 55])
    Color(rgba=[255, 204, 55, 255])
    Color(rgba=[0.127568, 0.566949, 0.550556])
    Color(rgba=[0.127568, 0.566949, 0.550556, 1.0])


def test_colors_rgbaf():
    Color(rgbaf=[1, 0.8, 0, 0.6])
    Color(rgbaf=[1, 0.8, 0.6])
    Color(rgbaf="0xFF3223")
    Color(rgbaf="0xFF322332")
    Color(rgbaf="#FF3223")
    Color(rgbaf="#FF322332")
    Color(rgbaf=[1, 0.8, 0.6])
    Color(rgbaf=[1, 0.8, 0.6, 1])
    Color(rgbaf=[0.127568, 0.566949, 0.550556])
    Color(rgbaf=[0.127568, 0.566949, 0.550556, 1.0])


def test_color_invalid_colors_rgba():
    with pytest.raises(TypeError):
        Color(rgba=[256, 204, 0, 55])
    with pytest.raises(TypeError):
        Color(rgba=[-204, 0, 55])
    with pytest.raises(TypeError):
        Color(rgba=[255, 204])
    with pytest.raises(TypeError):
        Color(rgba=[255, 232, 300])
    with pytest.raises(ValidationError):
        Color(rgba=-3)  # type: ignore


def test_color_invalid_colors_rgbaf():
    with pytest.raises(TypeError):
        Color(rgbaf=[256, 204, 0, 55])
    with pytest.raises(TypeError):
        Color(rgbaf=[-204, 0, 55])
    with pytest.raises(TypeError):
        Color(rgbaf=[255, 204])
    with pytest.raises(TypeError):
        Color(rgbaf=[255, 232, 300])
    with pytest.raises(ValidationError):
        Color(rgbaf=-3)  # type: ignore
    with pytest.raises(TypeError):
        Color(rgbaf=[255, 204, 55, 255, 42])
    with pytest.raises(TypeError):
        Color(rgbaf=[0.127568, 0.566949, 0.550556, 1.0, 3.0])


def test_material_image():
    expected_result = """{
    "image": {
        "image": "https://site.com/image.png",
        "repeat": [
            2,
            2
        ],
        "color": {
            "rgba": [
                200.0,
                100.0,
                30.0,
                255.0
            ]
        }
    }
}"""

    mat = Material(
        image=ImageMaterial(
            image=Uri(uri="https://site.com/image.png"),
            repeat=[2, 2],
            color=Color(rgba=[200, 100, 30]),
        )
    )
    assert str(mat) == expected_result


def test_material_image_uri():
    expected_result = """{
    "image": {
        "image": "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7",
        "repeat": [
            2,
            2
        ],
        "color": {
            "rgba": [
                200.0,
                100.0,
                30.0,
                255.0
            ]
        }
    }
}"""

    mat = Material(
        image=ImageMaterial(
            image=Uri(
                uri="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
            ),
            repeat=[2, 2],
            color=Color(rgba=[200, 100, 30]),
        )
    )
    assert str(mat) == expected_result


def test_material_grid():
    expected_result = """{
    "color": {
        "rgba": [
            20.0,
            20.0,
            30.0,
            255.0
        ]
    },
    "cellAlpha": 1.0,
    "lineCount": [
        16,
        16
    ],
    "lineThickness": [
        2.0,
        2.0
    ],
    "lineOffset": [
        0.3,
        0.4
    ]
}"""

    pol_mat = GridMaterial(
        color=Color(rgba=[20, 20, 30]),
        cellAlpha=1.0,
        lineCount=[16, 16],
        lineThickness=[2.0, 2.0],
        lineOffset=[0.3, 0.4],
    )
    assert str(pol_mat) == expected_result


def test_nested_delete():
    expected_result = """{
    "color": {
        "delete": true
    },
    "cellAlpha": 1.0,
    "lineCount": [
        16,
        16
    ],
    "lineThickness": [
        2.0,
        2.0
    ],
    "lineOffset": [
        0.3,
        0.4
    ]
}"""

    pol_mat = GridMaterial(
        color=Color(rgba=[20, 20, 30], delete=True),
        cellAlpha=1.0,
        lineCount=[16, 16],
        lineThickness=[2.0, 2.0],
        lineOffset=[0.3, 0.4],
    )
    assert str(pol_mat) == expected_result


def test_material_stripe():
    expected_result = """{
    "evenColor": {
        "rgba": [
            0.0,
            0.0,
            0.0,
            255.0
        ]
    },
    "oddColor": {
        "rgba": [
            255.0,
            255.0,
            255.0,
            255.0
        ]
    },
    "offset": 0.3,
    "repeat": 4.0
}"""

    pol_mat = StripeMaterial(
        evenColor=Color(rgba=[0, 0, 0]),
        oddColor=Color(rgba=[255, 255, 255]),
        offset=0.3,
        repeat=4.0,
    )
    assert str(pol_mat) == expected_result


def test_material_checkerboard():
    expected_result = """{
    "evenColor": {
        "rgba": [
            0.0,
            0.0,
            0.0,
            255.0
        ]
    },
    "oddColor": {
        "rgba": [
            255.0,
            255.0,
            255.0,
            255.0
        ]
    },
    "repeat": [
        4,
        4
    ]
}"""

    pol_mat = CheckerboardMaterial(
        evenColor=Color(rgba=[0, 0, 0]),
        oddColor=Color(rgba=[255, 255, 255]),
        repeat=[4, 4],
    )
    assert str(pol_mat) == expected_result


def test_position_has_delete():
    expected_result = """{
    "delete": true
}"""
    pos = Position(delete=True, cartesian=[0, 0, 0])
    assert pos.delete
    assert str(pos) == expected_result


def test_position_list_has_delete():
    expected_result = """{
    "delete": true
}"""
    pos = PositionList(delete=True, cartesian=[0, 0, 0])
    assert pos.delete
    assert str(pos) == expected_result


def test_position_list_of_lists_has_delete():
    expected_result = """{
    "delete": true
}"""
    pos = PositionListOfLists(
        delete=True, cartesian=[[20.0, 20.0, 0.0], [10.0, 10.0, 0.0]]
    )
    assert pos.delete
    assert str(pos) == expected_result


def test_position_no_values_raises_error():
    with pytest.raises(TypeError) as exc:
        Position()

    assert (
        "One of cartesian, cartographicDegrees, cartographicRadians or reference must be given"
        in exc.exconly()
    )


def test_position_list_of_lists_no_values_raises_error():
    with pytest.raises(TypeError) as exc:
        PositionListOfLists()

    assert (
        "One of cartesian, cartographicDegrees, cartographicRadians or references must be given"
        in exc.exconly()
    )


def test_position_list_no_values_raises_error():
    with pytest.raises(TypeError) as exc:
        PositionList()

    assert (
        "One of cartesian, cartographicDegrees, cartographicRadians or references must be given"
        in exc.exconly()
    )


def test_position_with_delete_has_nothing_else():
    expected_result = """{
    "delete": true
}"""
    pos_list = Position(delete=True, cartesian=[1, 2, 3])
    pos_val = Position(delete=True, cartesian=Cartesian3Value(values=[1, 2, 3]))
    assert str(pos_list) == str(pos_val) == expected_result
    pos_list = Position(delete=True, cartographicRadians=[1, 2, 3])
    pos_val = Position(
        delete=True, cartographicRadians=CartographicRadiansValue(values=[1, 2, 3])
    )
    assert str(pos_list) == str(pos_val) == expected_result
    pos_list = Position(delete=True, cartographicDegrees=[1, 2, 3])
    pos_val = Position(
        delete=True, cartographicDegrees=CartographicDegreesValue(values=[1, 2, 3])
    )
    assert str(pos_list) == str(pos_val) == expected_result
    pos_list = Position(delete=True, cartesianVelocity=[1, 2, 3, 4, 5, 6])
    pos_val = Position(
        delete=True,
        cartesianVelocity=Cartesian3VelocityValue(values=[1, 2, 3, 4, 5, 6]),
    )
    assert str(pos_list) == str(pos_val) == expected_result


def test_position_has_given_epoch():
    expected_epoch = format_datetime_like(
        dt.datetime(2019, 6, 11, 12, 26, 58, tzinfo=dt.timezone.utc)
    )

    pos = Position(epoch=expected_epoch, cartesian=[0, 0, 0])

    assert pos.epoch == expected_epoch


def test_positionlist_has_given_epoch():
    expected_epoch = format_datetime_like(
        dt.datetime(2019, 6, 11, 12, 26, 58, tzinfo=dt.timezone.utc)
    )

    pos = PositionList(epoch=expected_epoch, cartesian=[0, 0, 0])

    assert pos.epoch == expected_epoch


def test_position_renders_epoch():
    expected_result = """{
    "epoch": "2019-03-20T12:00:00.000000Z",
    "cartesian": [
        0.0,
        0.0,
        0.0
    ]
}"""
    pos = Position(
        epoch=dt.datetime(2019, 3, 20, 12, tzinfo=dt.timezone.utc), cartesian=[0, 0, 0]
    )

    assert str(pos) == expected_result


def test_position_cartographic_degrees():
    expected_result = """{
    "cartographicDegrees": [
        10.0,
        20.0,
        0.0
    ]
}"""
    pos = Position(cartographicDegrees=[10.0, 20.0, 0.0])

    assert str(pos) == expected_result


def test_position_reference():
    expected_result = """{
    "reference": "this#satellite"
}"""
    pos = Position(reference="this#satellite")
    assert str(pos) == expected_result
    pos = Position(reference=ReferenceValue(value="this#satellite"))
    assert str(pos) == expected_result


def test_viewfrom_reference():
    expected_result = """{
    "reference": "this#satellite"
}"""
    v = ViewFrom(reference="this#satellite")
    assert str(v) == expected_result
    v = ViewFrom(reference=ReferenceValue(value="this#satellite"))
    assert str(v) == expected_result


def test_viewfrom_cartesian():
    expected_result = """{
    "cartesian": [
        -1000.0,
        0.0,
        300.0
    ]
}"""
    v = ViewFrom(cartesian=Cartesian3Value(values=[-1000, 0, 300]))

    assert str(v) == expected_result


def test_viewfrom_has_delete():
    expected_result = """{
    "delete": true
}"""
    v = ViewFrom(delete=True, cartesian=[14.0, 12.0, 1.0])
    assert v.delete
    assert str(v) == expected_result


def test_viewfrom_no_values_raises_error():
    with pytest.raises(ValidationError) as _:
        ViewFrom()


def test_single_interval_value():
    expected_result = """{
    "interval": "2019-01-01T00:00:00.000000Z/2019-01-02T00:00:00.000000Z",
    "boolean": true
}"""

    start = dt.datetime(2019, 1, 1, tzinfo=dt.timezone.utc)
    end = dt.datetime(2019, 1, 2, tzinfo=dt.timezone.utc)

    prop = IntervalValue(start=start, end=end, value=True)

    assert str(prop) == expected_result


def test_multiple_interval_value():
    expected_result = """[
    {
        "interval": "2019-01-01T00:00:00.000000Z/2019-01-02T00:00:00.000000Z",
        "boolean": true
    },
    {
        "interval": "2019-01-02T00:00:00.000000Z/2019-01-03T00:00:00.000000Z",
        "boolean": false
    }
]"""

    start0 = dt.datetime(2019, 1, 1, tzinfo=dt.timezone.utc)
    end0 = start1 = dt.datetime(2019, 1, 2, tzinfo=dt.timezone.utc)
    end1 = dt.datetime(2019, 1, 3, tzinfo=dt.timezone.utc)

    prop = TimeIntervalCollection(
        values=[
            IntervalValue(start=start0, end=end0, value=True),
            IntervalValue(start=start1, end=end1, value=False),
        ]
    )

    assert str(prop) == expected_result


def test_multiple_interval_decimal_value():
    expected_result = """[
    {
        "interval": "2019-01-01T01:02:03.456789Z/2019-01-02T01:02:03.456789Z",
        "boolean": true
    },
    {
        "interval": "2019-01-02T01:02:03.456789Z/2019-01-03T01:02:03.456789Z",
        "boolean": false
    }
]"""

    start0 = dt.datetime(2019, 1, 1, 1, 2, 3, 456789, tzinfo=dt.timezone.utc)
    end0 = start1 = dt.datetime(2019, 1, 2, 1, 2, 3, 456789, tzinfo=dt.timezone.utc)
    end1 = dt.datetime(2019, 1, 3, 1, 2, 3, 456789, tzinfo=dt.timezone.utc)

    prop = TimeIntervalCollection(
        values=[
            IntervalValue(start=start0, end=end0, value=True),
            IntervalValue(start=start1, end=end1, value=False),
        ]
    )

    assert str(prop) == expected_result


def test_orientation():
    expected_result = """{
    "unitQuaternion": [
        0.0,
        0.0,
        0.0,
        1.0
    ]
}"""

    result = Orientation(unitQuaternion=UnitQuaternionValue(values=[0, 0, 0, 1]))

    assert str(result) == expected_result


def test_model():
    expected_result = """{
    "gltf": "https://sandcastle.cesium.com/SampleData/models/CesiumAir/Cesium_Air.glb"
}"""

    result = Model(
        gltf="https://sandcastle.cesium.com/SampleData/models/CesiumAir/Cesium_Air.glb"
    )
    result1 = Model(
        gltf=Uri(
            uri="https://sandcastle.cesium.com/SampleData/models/CesiumAir/Cesium_Air.glb"
        )
    )

    assert str(result) == str(result1) == expected_result


@pytest.mark.xfail
def test_bad_uri_raises_error():
    with pytest.raises(TypeError):
        Uri(uri="a")


def test_ellipsoid():
    expected_result = """{
    "radii": {
        "cartesian": [
            20.0,
            30.0,
            40.0
        ]
    },
    "fill": false,
    "outline": true
}"""

    ell = Ellipsoid(
        radii=EllipsoidRadii(cartesian=[20.0, 30.0, 40.0]), fill=False, outline=True
    )
    assert str(ell) == expected_result


def test_ellipsoid_parameters():
    expected_result = """{
    "radii": {
        "cartesian": [
            500000.0,
            500000.0,
            500000.0
        ]
    },
    "innerRadii": {
        "cartesian": [
            10000.0,
            10000.0,
            10000.0
        ]
    },
    "minimumClock": -15.0,
    "maximumClock": 15.0,
    "minimumCone": 75.0,
    "maximumCone": 105.0,
    "material": {
        "solidColor": {
            "color": {
                "rgba": [
                    255.0,
                    0.0,
                    0.0,
                    100.0
                ]
            }
        }
    },
    "outline": true,
    "outlineColor": {
        "rgbaf": [
            0.0,
            0.0,
            0.0,
            1.0
        ]
    }
}"""

    ell = Ellipsoid(
        radii=EllipsoidRadii(cartesian=[500000.0, 500000.0, 500000.0]),
        innerRadii=EllipsoidRadii(cartesian=[10000.0, 10000.0, 10000.0]),
        minimumClock=-15.0,
        maximumClock=15.0,
        minimumCone=75.0,
        maximumCone=105.0,
        material=Material(
            solidColor=SolidColorMaterial(color=Color(rgba=[255, 0, 0, 100])),
        ),
        outline=True,
        outlineColor=Color(rgbaf=[0, 0, 0, 1]),
    )
    assert str(ell) == expected_result


def test_polygon_with_hole():
    expected_result = """{
    "positions": {
        "cartographicDegrees": [
            30.0,
            40.0,
            1.0
        ]
    },
    "holes": {
        "cartographicDegrees": [
            [
                20.0,
                20.0,
                0.0
            ],
            [
                10.0,
                10.0,
                0.0
            ]
        ]
    }
}"""

    p = Polygon(
        positions=PositionList(cartographicDegrees=[30.0, 40.0, 1.0]),
        holes=PositionListOfLists(
            cartographicDegrees=[[20.0, 20.0, 0.0], [10.0, 10.0, 0.0]]
        ),
    )
    assert str(p) == expected_result


def test_polygon_interval():
    """This only tests one interval"""

    expected_result = """{
    "positions": {
        "cartographicDegrees": [
            10.0,
            20.0,
            0.0
        ],
        "interval": "2019-03-20T12:00:00.000000Z/2019-04-20T12:00:00.000000Z"
    }
}"""
    t = TimeInterval(
        start=dt.datetime(2019, 3, 20, 12, tzinfo=dt.timezone.utc),
        end=dt.datetime(2019, 4, 20, 12, tzinfo=dt.timezone.utc),
    )
    poly = Polygon(
        positions=PositionList(cartographicDegrees=[10.0, 20.0, 0.0], interval=t)
    )
    assert str(poly) == expected_result


def test_polygon_outline():
    expected_result = """{
    "positions": {
        "cartographicDegrees": [
            10.0,
            20.0,
            0.0
        ]
    },
    "material": {
        "solidColor": {
            "color": {
                "rgba": [
                    255.0,
                    100.0,
                    0.0,
                    100.0
                ]
            }
        }
    },
    "outlineColor": {
        "rgba": [
            0.0,
            0.0,
            0.0,
            255.0
        ]
    },
    "outline": true,
    "extrudedHeight": 0.0,
    "perPositionHeight": true
}"""
    poly = Polygon(
        positions=PositionList(cartographicDegrees=[10.0, 20.0, 0.0]),
        material=Material(
            solidColor=SolidColorMaterial(
                color=Color(
                    rgba=[255, 100, 0, 100],
                ),
            ),
        ),
        outlineColor=Color(
            rgba=[0, 0, 0, 255],
        ),
        outline=True,
        extrudedHeight=0,
        perPositionHeight=True,
    )
    assert str(poly) == expected_result


def test_polygon_interval_with_position():
    """This only tests one interval"""

    expected_result = """{
    "positions": {
        "cartographicDegrees": [
            10.0,
            20.0,
            0.0
        ],
        "interval": "2019-03-20T12:00:00.000000Z/2019-04-20T12:00:00.000000Z"
    }
}"""
    t = TimeInterval(
        start=dt.datetime(2019, 3, 20, 12, tzinfo=dt.timezone.utc),
        end=dt.datetime(2019, 4, 20, 12, tzinfo=dt.timezone.utc),
    )
    poly = Polygon(
        positions=PositionList(cartographicDegrees=[10.0, 20.0, 0.0], interval=t)
    )
    assert str(poly) == expected_result


def test_label_offset():
    expected_result = """{
    "pixelOffset": {
        "cartesian2": [
            5.0,
            5.0
        ]
    }
}"""

    label = Label(pixelOffset=Cartesian2Value(values=[5, 5]))
    assert str(label) == expected_result


def test_tileset():
    expected_result = """{
    "uri": "../SampleData/Cesium3DTiles/Batched/BatchedColors/tileset.json",
    "show": true
}"""
    tileset = Tileset(
        show=True, uri="../SampleData/Cesium3DTiles/Batched/BatchedColors/tileset.json"
    )
    tileset1 = Tileset(
        show=True,
        uri=Uri(uri="../SampleData/Cesium3DTiles/Batched/BatchedColors/tileset.json"),
    )
    assert str(tileset) == str(tileset1) == expected_result


def test_check_classes_with_references_ViewFrom():
    assert (
        str(ViewFrom(reference="this#that"))
        == """{
    "reference": "this#that"
}"""
    )
    assert (
        str(ViewFrom(reference=ReferenceValue(value="this#that")))
        == """{
    "reference": "this#that"
}"""
    )


def test_check_classes_with_references_EllipsoidRadii():
    assert (
        str(EllipsoidRadii(reference="this#that"))
        == str(EllipsoidRadii(reference=ReferenceValue(value="this#that")))
        == """{
    "reference": "this#that"
}"""
    )


def test_check_classes_with_references_ArcType():
    assert (
        str(ArcType(reference="this#that"))
        == str(ArcType(reference=ReferenceValue(value="this#that")))
        == """{
    "reference": "this#that"
}"""
    )


def test_check_classes_with_references_Position():
    assert (
        str(Position(reference="this#that"))
        == """{
    "reference": "this#that"
}"""
    )


def test_check_classes_with_references_Orientation():
    assert (
        str(Orientation(reference="this#that"))
        == str(Orientation(reference=ReferenceValue(value="this#that")))
        == """{
    "reference": "this#that"
}"""
    )


def test_check_classes_with_references_NearFarScalar():
    assert (
        str(NearFarScalar(reference="this#that"))
        == str(NearFarScalar(reference=ReferenceValue(value="this#that")))
        == """{
    "reference": "this#that"
}"""
    )


def test_check_classes_with_references_CornerType():
    assert (
        str(CornerType(reference="this#that"))
        == str(
            CornerType(
                reference=ReferenceValue(value="this#that"),
            )
        )
        == """{
    "reference": "this#that"
}"""
    )


def test_check_classes_with_references_ColorBlendMode():
    assert (
        str(ColorBlendMode(reference="this#that"))
        == str(
            ColorBlendMode(
                reference=ReferenceValue(value="this#that"),
            )
        )
        == """{
    "reference": "this#that"
}"""
    )


def test_check_classes_with_references_HeightReference():
    assert (
        str(HeightReference(reference="this#that"))
        == str(
            HeightReference(
                reference=ReferenceValue(value="this#that"),
            )
        )
        == """{
    "reference": "this#that"
}"""
    )


def test_check_classes_with_references_EyeOffset():
    assert (
        str(EyeOffset(reference="this#that"))
        == str(EyeOffset(reference=ReferenceValue(value="this#that")))
        == """{
    "reference": "this#that"
}"""
    )


def test_check_classes_with_references_RectangleCoordinates():
    assert (
        str(RectangleCoordinates(reference="this#that"))
        == """{
    "reference": "this#that"
}"""
    )


def test_check_classes_with_references_BoxDimensions():
    b1 = BoxDimensions(reference="this#that")
    b2 = BoxDimensions(reference="this#that")
    b3 = BoxDimensions(reference=ReferenceValue(value="this#that"))
    assert (
        str(b1)
        == str(b2)
        == str(b3)
        == """{
    "reference": "this#that"
}"""
    )


def test_check_classes_with_references_DistanceDisplayCondition():
    assert (
        str(
            DistanceDisplayCondition(
                reference="this#that",
            )
        )
        == str(
            DistanceDisplayCondition(
                reference=ReferenceValue(value="this#that"),
            )
        )
        == """{
    "reference": "this#that"
}"""
    )


def test_check_classes_with_references_ClassificationType():
    assert (
        str(ClassificationType(reference="this#that"))
        == str(
            ClassificationType(
                reference=ReferenceValue(value="this#that"),
            )
        )
        == """{
    "reference": "this#that"
}"""
    )


def test_check_classes_with_references_ShadowMode():
    assert (
        str(ShadowMode(reference="this#that"))
        == str(
            ShadowMode(
                reference=ReferenceValue(value="this#that"),
            )
        )
        == """{
    "reference": "this#that"
}"""
    )


def test_rectangle_coordinates_delete():
    assert (
        str(RectangleCoordinates(wsen=[0, 0], reference="this#that", delete=True))
        == """{
    "delete": true
}"""
    )


def test_different_positions():
    pos1 = Position(cartographicDegrees=[1, 2, 3])
    pos2 = Position(cartographicRadians=[1, 2, 3])
    assert pos1 != pos2
    assert str(pos1) != str(pos2)


def test_positionlist_bad_cartesian():
    with pytest.raises(TypeError):
        PositionList(cartesian=[0, 0, 0, 0, 0])
    with pytest.raises(TypeError):
        PositionList(cartesian=[0, 0])
    with pytest.raises(TypeError):
        PositionList(cartesian=[0])
    with pytest.raises(ValueError):
        PositionList(cartesian=[])


def test_positionlist_bad_cartographicRadians():
    with pytest.raises(TypeError):
        PositionList(cartographicRadians=[0, 0, 0, 0, 0])
    with pytest.raises(TypeError):
        PositionList(cartographicRadians=[0, 0])
    with pytest.raises(TypeError):
        PositionList(cartographicRadians=[0])
    with pytest.raises(ValueError):
        PositionList(cartographicRadians=[])


def test_positionlist_bad_cartographicDegrees():
    with pytest.raises(TypeError):
        PositionList(cartographicDegrees=[0, 0, 0, 0, 0])
    with pytest.raises(TypeError):
        PositionList(cartographicDegrees=[0, 0])
    with pytest.raises(TypeError):
        PositionList(cartographicDegrees=[0])
    with pytest.raises(ValueError):
        PositionList(cartographicDegrees=[])


def test_position_bad_cartesian():
    with pytest.raises(TypeError):
        Position(cartesian=[0, 0])
    with pytest.raises(TypeError):
        Position(cartesian=[0])
    with pytest.raises(ValueError):
        Position(cartesian=[])


def test_position_bad_cartographicRadians():
    with pytest.raises(TypeError):
        Position(cartographicRadians=[0, 0])
    with pytest.raises(TypeError):
        Position(cartographicRadians=[0])
    with pytest.raises(ValueError):
        Position(cartographicRadians=[])


def test_position_bad_cartographicDegrees():
    with pytest.raises(TypeError):
        Position(cartographicDegrees=[0, 0])
    with pytest.raises(TypeError):
        Position(cartographicDegrees=[0])
    with pytest.raises(ValueError):
        Position(cartographicDegrees=[])


def test_position_bad_cartesianVelocity():
    with pytest.raises(TypeError):
        Position(cartesianVelocity=[0, 0, 0, 0])
    with pytest.raises(TypeError):
        Position(cartesianVelocity=[0, 0])
    with pytest.raises(TypeError):
        Position(cartesianVelocity=[0])
    with pytest.raises(ValueError):
        Position(cartesianVelocity=[])


def test_position_bad_multipleTypes():
    with pytest.raises(TypeError):
        Position(cartesian=[0], reference=ReferenceValue(value="1#this"))
    with pytest.raises(TypeError):
        Position(cartographicRadians=[0], reference=ReferenceValue(value="1#this"))
    with pytest.raises(TypeError):
        Position(cartographicDegrees=[0], reference=ReferenceValue(value="1#this"))
    with pytest.raises(TypeError):
        Position(cartesianVelocity=[0], reference=ReferenceValue(value="1#this"))

    with pytest.raises(TypeError):
        Position(cartesian=[0], reference="1#this")
    with pytest.raises(TypeError):
        Position(cartographicRadians=[0], reference="1#this")
    with pytest.raises(TypeError):
        Position(cartographicDegrees=[0], reference="1#this")
    with pytest.raises(TypeError):
        Position(cartesianVelocity=[0], reference="1#this")


def test_no_values():
    with pytest.raises(ValueError):
        Color(rgba=[])


def test_SequenceTime_mix():
    with pytest.raises(ValidationError):
        TimeIntervalCollection(
            values=[  # type: ignore
                TimeInterval(
                    start=dt.datetime(2019, 3, 20, 12, tzinfo=dt.timezone.utc),
                    end=dt.datetime(2019, 4, 20, 12, tzinfo=dt.timezone.utc),
                ),
                IntervalValue(
                    start=dt.datetime(2019, 3, 20, 12, tzinfo=dt.timezone.utc),
                    end=dt.datetime(2019, 4, 20, 12, tzinfo=dt.timezone.utc),
                    value=True,
                ),
            ]
        )


def test_bad_PositionListOfLists():
    with pytest.raises(TypeError):
        PositionListOfLists(
            cartographicDegrees=[[20.0, 20.0, 0.0], [10.0, 10.0, 0.0, 0]]
        )
    with pytest.raises(ValidationError):
        PositionListOfLists(cartographicDegrees=[])
    with pytest.raises(ValidationError):
        PositionListOfLists(cartographicDegrees=[[0, 0, 0], []])


def test_bad_PositionList():
    with pytest.raises(TypeError):
        PositionList(cartographicDegrees=[10.0, 10.0, 0.0, 0])
    with pytest.raises(ValidationError):
        PositionList(cartographicDegrees=[])
    with pytest.raises(TypeError):
        PositionList(cartographicDegrees=[0, 0, 0, 0, 0])


def test_bad_Position():
    with pytest.raises(ValidationError):
        Position(cartographicDegrees=[])
    with pytest.raises(TypeError):
        Position(cartographicDegrees=[0, 0, 0, 0, 0])


def test_position_list_with_cartesian():
    expected_result = """{
    "cartesian": [
        1.0,
        2.0,
        3.0,
        4.0,
        5.0,
        6.0
    ]
}"""

    p1 = PositionList(cartesian=Cartesian3ListValue(values=[1, 2, 3, 4, 5, 6]))
    assert str(p1) == expected_result


def test_position_list_with_cartographicRadians():
    expected_result = """{
    "cartographicRadians": [
        1.0,
        2.0,
        3.0
    ]
}"""

    p1 = PositionList(
        cartographicRadians=CartographicRadiansListValue(values=[1, 2, 3])
    )
    assert str(p1) == expected_result


def test_position_list_with_cartographicDegrees():
    expected_result = """{
    "cartographicDegrees": [
        1.0,
        2.0,
        3.0
    ]
}"""

    p1 = PositionList(
        cartographicDegrees=CartographicDegreesListValue(values=[1, 2, 3])
    )
    assert str(p1) == expected_result


def test_position_list_with_references():
    expected_result = """{
    "references": [
        "1#this"
    ]
}"""
    p1 = PositionList(
        references=["1#this"],
    )
    p2 = PositionList(
        references=ReferenceListValue(values=["1#this"]),
    )
    assert str(p1) == str(p2) == expected_result
    expected_result = """{
    "references": [
        "1#this"
    ]
}"""


def test_position_list_with_references_extra_arguments():
    with pytest.raises(TypeError):
        PositionList(
            references=ReferenceListValue(values=["1#this"]),
            cartesian=[0, 0, 0],
        )


def test_position_list_with_bad_references():
    with pytest.raises(TypeError):
        PositionList(
            cartographicDegrees=CartographicDegreesListValue(values=[20, 30, 10]),
            references=["1#this", "1#this"],
        )


def test_position_list_of_lists_with_cartesian():
    expected_result = """{
    "cartesian": [
        [
            1.0,
            2.0,
            3.0
        ]
    ]
}"""

    p1 = PositionListOfLists(cartesian=Cartesian3ListOfListsValue(values=[[1, 2, 3]]))
    assert str(p1) == expected_result


def test_position_list_of_lists_with_cartographicRadians():
    expected_result = """{
    "cartographicRadians": [
        [
            1.0,
            2.0,
            3.0
        ]
    ]
}"""

    p1 = PositionListOfLists(
        cartographicRadians=CartographicRadiansListOfListsValue(values=[[1, 2, 3]])
    )
    assert str(p1) == expected_result


def test_position_list_of_lists_with_cartographicDegrees():
    expected_result = """{
    "cartographicDegrees": [
        [
            1.0,
            2.0,
            3.0
        ]
    ]
}"""

    p1 = PositionListOfLists(
        cartographicDegrees=CartographicDegreesListOfListsValue(values=[[1, 2, 3]])
    )
    assert str(p1) == expected_result


def test_position_list_of_lists_with_references():
    expected_result = """{
    "references": [
        [
            "1#this"
        ],
        [
            "1#this"
        ]
    ]
}"""
    p1 = PositionListOfLists(
        references=[["1#this"], ["1#this"]],
    )
    p2 = PositionListOfLists(
        references=ReferenceListOfListsValue(values=[["1#this"], ["1#this"]]),
    )
    assert str(p1) == str(p2) == expected_result


def test_position_list_of_lists_with_bad_references():
    with pytest.raises(TypeError):
        PositionListOfLists(
            cartographicDegrees=CartographicDegreesListOfListsValue(
                values=[[20, 30, 10], [20, 30, 10]]
            ),
            references=[["1#this"], ["1#this"], ["2#this"]],
        )
    with pytest.raises(TypeError):
        PositionListOfLists(
            cartographicDegrees=CartographicDegreesListOfListsValue(
                values=[[20, 30, 10], [20, 30, 10]]
            ),
            references=ReferenceListOfListsValue(
                values=[["1#this"], ["1#this", "2#this"]]
            ),
        )


def test_check_increasing_time():
    with pytest.raises(TypeError):
        Cartesian3Value(values=[0, 0, 0, 0, 1, 0, 0, 0, 2, 0, 0, 0, 1, 0, 0, 0])


def test_packet_billboard():
    expected_result = """{
    "image": "file://image.png",
    "eyeOffset": {
        "cartesian": [
            1.0,
            2.0,
            3.0
        ]
    }
}"""
    packet = Billboard(
        image="file://image.png",
        eyeOffset=EyeOffset(cartesian=Cartesian3Value(values=[1, 2, 3])),
    )
    assert str(packet) == expected_result
    packet = Billboard(image="file://image.png", eyeOffset=[1, 2, 3])
    assert str(packet) == expected_result


def test_packet_billboard_further():
    expected_result = """{
    "image": "file://image.png",
    "eyeOffset": {
        "cartesian": [
            1.0,
            2.0,
            3.0
        ]
    },
    "rotation": 0.1,
    "sizeInMeters": true,
    "width": 10.0,
    "height": 10.0,
    "scaleByDistance": {
        "nearFarScalar": [
            150.0,
            2.0,
            15000000.0,
            0.5
        ]
    },
    "translucencyByDistance": {
        "nearFarScalar": [
            250.0,
            2.0,
            15000000.0,
            0.5
        ]
    },
    "pixelOffsetScaleByDistance": {
        "nearFarScalar": [
            350.0,
            2.0,
            15000000.0,
            0.5
        ]
    },
    "distanceDisplayCondition": {
        "distanceDisplayCondition": [
            14.0,
            81.0
        ]
    },
    "disableDepthTestDistance": 2.0
}"""
    packet = Billboard(
        image="file://image.png",
        eyeOffset=EyeOffset(cartesian=Cartesian3Value(values=[1, 2, 3])),
        rotation=0.1,
        sizeInMeters=True,
        width=10,
        height=10,
        scaleByDistance=NearFarScalar(
            nearFarScalar=NearFarScalarValue(values=[150, 2.0, 15000000, 0.5])
        ),
        translucencyByDistance=NearFarScalar(
            nearFarScalar=NearFarScalarValue(values=[250, 2.0, 15000000, 0.5])
        ),
        pixelOffsetScaleByDistance=NearFarScalar(
            nearFarScalar=NearFarScalarValue(values=[350, 2.0, 15000000, 0.5])
        ),
        disableDepthTestDistance=2,
        distanceDisplayCondition=DistanceDisplayCondition(
            distanceDisplayCondition=DistanceDisplayConditionValue(values=[14, 81])
        ),
    )
    assert str(packet) == expected_result


def test_delete():
    expected_result = """{
    "delete": true
}"""
    p = PositionList(
        cartographicDegrees=CartographicDegreesListValue(values=[20, 30, 10]),
        delete=True,
    )
    assert str(p) == expected_result


def test_forbid_extras():
    with pytest.raises(ValidationError):
        PositionList(
            cartographicDegrees=CartographicDegreesListValue(values=[20, 30, 10]),
            delete=True,
            a=1,  # type: ignore[call-arg]
        )


# @pytest.mark.xfail(reason="Reference value needs further clarifying")
# def test_uri_ref():
#     expected_result = """{
#     "uri": "file://image.png",
#     "reference": "this#that"
# }"""
#     uri = Uri(uri="file://image.png", reference="this#that")
#     uri1 = Uri(uri="file://image.png", reference=ReferenceValue(value="this#that"))
#     assert str(uri) == str(uri1) == expected_result


def test_bad_color():
    with pytest.raises(TypeError):
        Color(rgba=[0, 0, 0, 0], rgbaf=[0, 0, 0, 0])
    with pytest.raises(TypeError):
        Color(rgba=[0, 0, 0, 0], reference="this#that")
    with pytest.raises(TypeError):
        Color(rgba=[0, 0, 0, 0], reference=ReferenceValue(value="this#that"))
    with pytest.raises(TypeError):
        Color(rgbaf=[0, 0, 0, 0], reference="this#that")
    with pytest.raises(TypeError):
        Color(rgbaf=[0, 0, 0, 0], reference=ReferenceValue(value="this#that"))
    with pytest.raises(TypeError):
        Color(rgbaf=[0, 0, 0, 0], rgba=[0, 0, 0, 0], reference="this#that")
    with pytest.raises(TypeError):
        Color(
            rgbaf=[0, 0, 0, 0],
            rgba=[0, 0, 0, 0],
            reference=ReferenceValue(value="this#that"),
        )


def test_bad_EllipsoidRadii():
    with pytest.raises(TypeError):
        EllipsoidRadii(cartesian=[0, 0, 0], reference="this#that")
    with pytest.raises(TypeError):
        EllipsoidRadii(cartesian=[0, 0, 0], reference=ReferenceValue(value="this#that"))


def test_bad_ArcType():
    with pytest.raises(TypeError):
        ArcType(arcType=ArcTypes.GEODESIC, reference="this#that")
    with pytest.raises(TypeError):
        ArcType(arcType=ArcTypes.GEODESIC, reference=ReferenceValue(value="this#that"))


def test_bad_ShadowMode():
    with pytest.raises(TypeError):
        ShadowMode(shadowMode=ShadowModes.DISABLED, reference="this#that")
    with pytest.raises(TypeError):
        ShadowMode(
            shadowMode=ShadowModes.DISABLED, reference=ReferenceValue(value="this#that")
        )


def test_bad_HeightReference():
    with pytest.raises(TypeError):
        HeightReference(heightReference=HeightReferences.NONE, reference="this#that")
    with pytest.raises(TypeError):
        HeightReference(
            heightReference=HeightReferences.NONE,
            reference=ReferenceValue(value="this#that"),
        )


def test_bad_ColorBlendMode():
    with pytest.raises(TypeError):
        ColorBlendMode(colorBlendMode=ColorBlendModes.HIGHLIGHT, reference="this#that")
    with pytest.raises(TypeError):
        ColorBlendMode(
            colorBlendMode=ColorBlendModes.HIGHLIGHT,
            reference=ReferenceValue(value="this#that"),
        )


def test_bad_CornerType():
    with pytest.raises(TypeError):
        CornerType(cornerType=CornerTypes.BEVELED, reference="this#that")
    with pytest.raises(TypeError):
        CornerType(
            cornerType=CornerTypes.BEVELED, reference=ReferenceValue(value="this#that")
        )


def test_bad_DistanceDisplayCondition():
    with pytest.raises(TypeError):
        DistanceDisplayCondition(
            distanceDisplayCondition=DistanceDisplayConditionValue(values=[14, 81]),
            reference="this#that",
        )
    with pytest.raises(TypeError):
        DistanceDisplayCondition(
            distanceDisplayCondition=DistanceDisplayConditionValue(values=[14, 81]),
            reference=ReferenceValue(value="this#that"),
        )


def test_bad_BoxDimensions():
    with pytest.raises(TypeError):
        BoxDimensions(cartesian=[14, 81, 0], reference="this#that")
    with pytest.raises(TypeError):
        BoxDimensions(
            cartesian=[14, 81, 0], reference=ReferenceValue(value="this#that")
        )


def test_bad_EyeOffset():
    with pytest.raises(TypeError):
        EyeOffset(cartesian=[14, 81, 0], reference="this#that")
    with pytest.raises(TypeError):
        EyeOffset(cartesian=[14, 81, 0], reference=ReferenceValue(value="this#that"))


def test_bad_Orientation():
    with pytest.raises(TypeError):
        Orientation(unitQuaternion=[14, 0, 81, 0], reference="this#that")
    with pytest.raises(TypeError):
        Orientation(
            unitQuaternion=[14, 0, 81, 0], reference=ReferenceValue(value="this#that")
        )


def test_bad_Uri():
    with pytest.raises(TypeError):
        Uri(uri="https://site.com/image.png", reference="this#that")
    with pytest.raises(TypeError):
        Uri(
            uri="https://site.com/image.png",
            reference=ReferenceValue(value="this#that"),
        )


def test_bad_NearFarScalar():
    with pytest.raises(TypeError):
        NearFarScalar(
            nearFarScalar=NearFarScalarValue(values=[350, 2.0, 15000000, 0.5]),
            reference="this#that",
        )
    with pytest.raises(TypeError):
        NearFarScalar(
            nearFarScalar=NearFarScalarValue(values=[350, 2.0, 15000000, 0.5]),
            reference=ReferenceValue(value="this#that"),
        )


def test_bad_RectangleCoordinates():
    with pytest.raises(TypeError):
        RectangleCoordinates(wsen=[81, 0], wsenDegrees=[81, 0], reference="this#that")
    with pytest.raises(TypeError):
        RectangleCoordinates(
            wsen=[81, 0],
            wsenDegrees=[81, 0],
            reference=ReferenceValue(value="this#that"),
        )
    with pytest.raises(TypeError):
        RectangleCoordinates(wsen=[81, 0], wsenDegrees=[81, 0])
    with pytest.raises(TypeError):
        RectangleCoordinates(wsenDegrees=[81, 0], reference="this#that")
    with pytest.raises(TypeError):
        RectangleCoordinates(
            wsenDegrees=[81, 0], reference=ReferenceValue(value="this#that")
        )
    with pytest.raises(TypeError):
        RectangleCoordinates(wsen=[81, 0], reference="this#that")
    with pytest.raises(TypeError):
        RectangleCoordinates(wsen=[81, 0], reference=ReferenceValue(value="this#that"))


def test_bad_ClassificationType():
    with pytest.raises(TypeError):
        ClassificationType(
            classificationType=ClassificationTypes.BOTH, reference="this#that"
        )
    with pytest.raises(TypeError):
        ClassificationType(
            classificationType=ClassificationTypes.BOTH,
            reference=ReferenceValue(value="this#that"),
        )


def test_ReferenceValue_is_reference():
    assert str(ClassificationType(reference="this#that")) == str(
        ClassificationType(reference=ReferenceValue(value="this#that"))
    )
    assert str(NearFarScalar(reference="this#that")) == str(
        NearFarScalar(reference=ReferenceValue(value="this#that"))
    )
    assert str(DistanceDisplayCondition(reference="this#that")) == str(
        DistanceDisplayCondition(reference=ReferenceValue(value="this#that"))
    )
    assert str(Color(reference="this#that")) == str(
        Color(reference=ReferenceValue(value="this#that"))
    )

    assert str(Color(reference="this#that")) == str(
        Color(reference=ReferenceValue(value="this#that"))
    )

    assert str(Color(reference="this#that")) == str(
        Color(reference=ReferenceValue(value="this#that"))
    )

    assert str(EllipsoidRadii(reference="this#that")) == str(
        EllipsoidRadii(reference=ReferenceValue(value="this#that"))
    )

    assert str(ArcType(reference="this#that")) == str(
        ArcType(reference=ReferenceValue(value="this#that"))
    )

    assert str(ShadowMode(reference="this#that")) == str(
        ShadowMode(reference=ReferenceValue(value="this#that"))
    )

    assert str(HeightReference(reference="this#that")) == str(
        HeightReference(reference=ReferenceValue(value="this#that"))
    )

    assert str(ColorBlendMode(reference="this#that")) == str(
        ColorBlendMode(reference=ReferenceValue(value="this#that"))
    )

    assert str(CornerType(reference="this#that")) == str(
        CornerType(reference=ReferenceValue(value="this#that"))
    )

    assert str(BoxDimensions(reference="this#that")) == str(
        BoxDimensions(reference=ReferenceValue(value="this#that"))
    )

    assert str(EyeOffset(reference="this#that")) == str(
        EyeOffset(reference=ReferenceValue(value="this#that"))
    )

    assert str(Orientation(reference="this#that")) == str(
        Orientation(reference=ReferenceValue(value="this#that"))
    )

    assert str(Uri(reference="this#that")) == str(
        Uri(reference=ReferenceValue(value="this#that"))
    )

    assert str(RectangleCoordinates(reference="this#that")) == str(
        RectangleCoordinates(reference=ReferenceValue(value="this#that"))
    )

    assert str(RectangleCoordinates(reference="this#that")) == str(
        RectangleCoordinates(reference=ReferenceValue(value="this#that"))
    )

    assert str(RectangleCoordinates(reference="this#that")) == str(
        RectangleCoordinates(reference=ReferenceValue(value="this#that"))
    )


def test_EllipsoidRadii_delete():
    expected_result = """{
    "delete": true
}"""
    p = EllipsoidRadii(delete=True, cartesian=[0, 0, 0])
    assert p.delete
    assert str(p) == expected_result


def test_ArcType_delete():
    expected_result = """{
    "delete": true
}"""
    p = ArcType(delete=True, reference="this#that")
    assert p.delete
    assert str(p) == expected_result


def test_ShadowMode_delete():
    expected_result = """{
    "delete": true
}"""
    p = ShadowMode(delete=True, reference="this#that")
    assert p.delete
    assert str(p) == expected_result


def test_ClassificationType_delete():
    expected_result = """{
    "delete": true
}"""
    p = ClassificationType(delete=True, reference="this#that")
    assert p.delete
    assert str(p) == expected_result


def test_DistanceDisplayCondition_delete():
    expected_result = """{
    "delete": true
}"""
    p = DistanceDisplayCondition(delete=True, reference="this#that")
    assert p.delete
    assert str(p) == expected_result


def test_BoxDimensions_delete():
    expected_result = """{
    "delete": true
}"""
    p = BoxDimensions(delete=True, reference="this#that")
    assert p.delete
    assert str(p) == expected_result


def test_EyeOffset_delete():
    expected_result = """{
    "delete": true
}"""
    p = EyeOffset(delete=True, reference="this#that")
    assert p.delete
    assert str(p) == expected_result


def test_HeightReference_delete():
    expected_result = """{
    "delete": true
}"""
    p = HeightReference(delete=True, reference="this#that")
    assert p.delete
    assert str(p) == expected_result


def test_ColorBlendMode_delete():
    expected_result = """{
    "delete": true
}"""
    p = ColorBlendMode(delete=True, reference="this#that")
    assert p.delete
    assert str(p) == expected_result


def test_CornerType_delete():
    expected_result = """{
    "delete": true
}"""
    p = CornerType(delete=True, reference="this#that")
    assert p.delete
    assert str(p) == expected_result


def test_NearFarScalar_delete():
    expected_result = """{
    "delete": true
}"""
    p = NearFarScalar(delete=True, reference="this#that")
    assert p.delete
    assert str(p) == expected_result


def test_Orientation_delete():
    expected_result = """{
    "delete": true
}"""
    p = Orientation(delete=True, reference="this#that")
    assert p.delete
    assert str(p) == expected_result


def test_Uri_delete():
    expected_result = """{
    "delete": true
}"""
    p = Uri(delete=True, reference="this#that")
    assert p.delete
    assert str(p) == expected_result
