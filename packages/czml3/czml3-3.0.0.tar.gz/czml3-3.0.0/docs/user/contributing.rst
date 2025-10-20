Contributing
============

This page details the features/properties that are missing from ``czml3``. The lists are incomplete.

Missing CZML Properties
-----------------------
* `LineOffset <https://github.com/AnalyticalGraphicsInc/czml-writer/wiki/LineOffset>`_
* `LineThickness <https://github.com/AnalyticalGraphicsInc/czml-writer/wiki/LineThickness>`_
* `LineCount <https://github.com/AnalyticalGraphicsInc/czml-writer/wiki/LineCount>`_
* `Repeat <https://github.com/AnalyticalGraphicsInc/czml-writer/wiki/Repeat>`_
* `NodeTransformations <https://github.com/AnalyticalGraphicsInc/czml-writer/wiki/NodeTransformations>`_
* `Articulations <https://github.com/AnalyticalGraphicsInc/czml-writer/wiki/Articulations>`_
* `PixelOffset <https://github.com/AnalyticalGraphicsInc/czml-writer/wiki/PixelOffset>`_
* `VelocityReferenceValue <https://github.com/AnalyticalGraphicsInc/czml-writer/wiki/VelocityReferenceValue>`_
* `Font <https://github.com/AnalyticalGraphicsInc/czml-writer/wiki/Font>`_
* `BackgroundPadding <https://github.com/AnalyticalGraphicsInc/czml-writer/wiki/BackgroundPadding>`_
* `CartographicRectangleRadiansValue <https://github.com/AnalyticalGraphicsInc/czml-writer/wiki/CartographicRectangleRadiansValue>`_
* `CartographicRectangleDegreesValue <https://github.com/AnalyticalGraphicsInc/czml-writer/wiki/CartographicRectangleDegreesValue>`_
* `CustomProperties <https://github.com/AnalyticalGraphicsInc/czml-writer/wiki/CustomProperties>`_
* `CustomProperty <https://github.com/AnalyticalGraphicsInc/czml-writer/wiki/CustomProperty>`_
* `PolylineVolume <https://github.com/AnalyticalGraphicsInc/czml-writer/wiki/PolylineVolume>`_
* `UriValue <https://github.com/AnalyticalGraphicsInc/czml-writer/wiki/UriValue>`_


CZML Properties With Missing Inputs
-----------------------------------
* `Packet <https://github.com/AnalyticalGraphicsInc/czml-writer/wiki/Packet>`_
* `Billboard <https://github.com/AnalyticalGraphicsInc/czml-writer/wiki/Billboard>`_
* `Label <https://github.com/AnalyticalGraphicsInc/czml-writer/wiki/Label>`_
* `Rectangle <https://github.com/AnalyticalGraphicsInc/czml-writer/wiki/Rectangle>`_
* `Polyline <https://github.com/AnalyticalGraphicsInc/czml-writer/wiki/Polyline>`_
* `InterpolatableProperty <https://github.com/AnalyticalGraphicsInc/czml-writer/wiki/InterpolatableProperty>`_

Broken Validations
------------------
- The ``Uri._check_uri`` does not check base64 images correctly.
- The ``Uri._check_uri`` does not allow relative paths, which seems to be supported despite it not being a valid uri value.
- The ``Uri.reference`` is stated in the `CZML documentation <https://github.com/AnalyticalGraphicsInc/czml-writer/wiki/Uri>`_ but ``Uri`` returns only the ``uri`` property.