"""Wires for electrical manhattan routes."""

from __future__ import annotations

from typing import Any

import numpy as np

import gdsfactory as gf
from gdsfactory.component import Component
from gdsfactory.cross_section import (
    port_names_electrical,
    port_types_electrical,
)
from gdsfactory.typings import CrossSectionSpec, LayerSpec, PortNames, PortTypes


@gf.cell_with_module_name
def wire_corner(
    cross_section: CrossSectionSpec = "metal_routing",
    port_names: PortNames = port_names_electrical,
    port_types: PortTypes = port_types_electrical,
    width: float | None = None,
    radius: float | None = None,
) -> Component:
    """Returns 45 degrees electrical corner wire.

    Args:
        cross_section: spec.
        port_names: port names.
        port_types: port types.
        width: optional width. Defaults to cross_section width.
        radius: ignored.
    """
    if width:
        x = gf.get_cross_section(cross_section, width=width)
    else:
        x = gf.get_cross_section(cross_section)

    layer = x.layer
    assert layer is not None
    width = x.width

    c = Component()
    a = width / 2
    xpts = [-a, a, a, -a]
    ypts = [-a, -a, a, a]
    c.add_polygon(list(zip(xpts, ypts, strict=False)), layer=layer)
    c.add_port(
        name=port_names[0],
        center=(-a, 0),
        width=width,
        orientation=180,
        layer=layer,
        port_type=port_types[0],
    )
    c.add_port(
        name=port_names[1],
        center=(0, a),
        width=width,
        orientation=90,
        layer=layer,
        port_type=port_types[1],
    )
    c.info["length"] = width
    c.info["dy"] = width
    x.add_bbox(c)
    return c


@gf.cell
def wire_corner45_straight(
    width: float | None = None,
    radius: float | None = None,
    cross_section: CrossSectionSpec = "metal_routing",
) -> gf.Component:
    """Returns 45 degrees wire straight ends.

    Args:
        width: of the wire.
        radius: of the corner. Defaults to width.
        cross_section: metal_routing.
    """
    c = gf.Component()
    xs = gf.get_cross_section(cross_section)
    radius = radius or xs.radius

    if radius is None:
        raise ValueError("Either radius or width must be specified")

    p = gf.Path(
        [
            (0.0, 0.0),
            (radius / 2.0, 0.0),
            (radius, radius / 2.0),
            (radius, radius),
        ]
    )

    if width:
        xs = gf.get_cross_section(cross_section, width=width)
    else:
        xs = gf.get_cross_section(cross_section)
    c = p.extrude(cross_section=xs)
    return c


@gf.cell_with_module_name
def wire_corner45(
    cross_section: CrossSectionSpec = "metal_routing",
    radius: float = 10,
    width: float | None = None,
    layer: LayerSpec | None = None,
    with_corner90_ports: bool = True,
) -> Component:
    """Returns 90 degrees electrical corner wire.

    Args:
        cross_section: spec.
        radius: in um.
        width: optional width.
        layer: optional layer.
        with_corner90_ports: if True adds ports at 90 degrees.
    """
    if width:
        x = gf.get_cross_section(cross_section, width=width)
    else:
        x = gf.get_cross_section(cross_section)
    layer = layer or x.layer
    assert layer is not None
    width = width or x.width
    radius = radius or width

    c = Component()
    a = width / 2
    xpts = [0, radius + a, radius + a, -np.sqrt(2) * width]
    ypts = [-a, radius, radius + np.sqrt(2) * width, -a]
    c.add_polygon(list(zip(xpts, ypts, strict=False)), layer=layer)

    if with_corner90_ports:
        c.add_port(
            name="e1",
            center=(0, 0),
            width=width,
            orientation=180,
            layer=layer,
            port_type="electrical",
        )
        c.add_port(
            name="e2",
            center=(radius, radius),
            width=width,
            orientation=90,
            layer=layer,
            port_type="electrical",
        )

    else:
        w = float(np.round(width * np.sqrt(2), 3))

        c.add_port(
            name="e1",
            center=(-w / 2, -a),
            width=w,
            orientation=270,
            layer=layer,
            port_type="electrical",
        )
        c.add_port(
            name="e2",
            center=(radius + a, radius + w / 2),
            width=w,
            orientation=0,
            layer=layer,
            port_type="electrical",
        )
    c.info["length"] = float(np.sqrt(2) * radius)
    return c


@gf.cell_with_module_name
def wire_corner_sections(
    cross_section: CrossSectionSpec = "metal_routing",
    port_type: str = "electrical",
    **kwargs: Any,
) -> Component:
    """Returns 90 degrees electrical corner wire, where all cross_section sections properly represented.

    Works well with symmetric cross_sections, not quite ready for asymmetric.

    Args:
        cross_section: spec.
        port_type: "electrical" or "optical".
        kwargs: cross_section settings, ignored (such as radius, width, layer).
    """
    x = gf.get_cross_section(cross_section)

    xmin, ymax = x.get_xmin_xmax()

    main_section = x.sections[0]

    all_sections = [main_section]
    all_sections.extend(x.sections)

    c = Component()

    for section in all_sections:
        layer = section.layer
        width = section.width
        offset = section.offset
        b = width / 2

        xpts = [xmin, offset - b, offset - b, offset + b, offset + b, xmin]
        ypts = [
            -offset + b,
            -offset + b,
            ymax,
            ymax,
            -offset - b,
            -offset - b,
        ]

        assert layer is not None

        c.add_polygon(list(zip(xpts, ypts, strict=False)), layer=layer)

    c.add_port(
        name="e1",
        center=(xmin, -(xmin + ymax) / 2),
        orientation=180,
        cross_section=x,
        layer=x.layer,
        port_type=port_type,
    )
    c.add_port(
        name="e2",
        center=((xmin + ymax) / 2, ymax),
        orientation=90,
        cross_section=x,
        layer=x.layer,
        port_type=port_type,
    )
    c.info["length"] = ymax - xmin
    c.info["dy"] = ymax - xmin
    x.add_bbox(c)
    return c
