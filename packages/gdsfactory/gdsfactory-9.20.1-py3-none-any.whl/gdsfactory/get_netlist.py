"""Extract netlist from component port connectivity.

Assumes two ports are connected when they have same width, x, y

.. code:: yaml

    connections:
        - coupler,N0:bendLeft,W0
        - coupler,N1:bendRight,N0
        - bednLeft,N0:straight,W0
        - bendRight,N0:straight,E0

    ports:
        - coupler,E0
        - coupler,W0

"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable, Sequence
from hashlib import md5
from pprint import pprint
from typing import Any, Protocol
from warnings import warn

import numpy as np
from kfactory import DInstance, LayerEnum, ProtoTKCell, VInstance, VKCell
from kfactory.kcell import AnyKCell, TKCell

from gdsfactory import Port, typings
from gdsfactory.component import (
    Component,
    ComponentAllAngle,
    ComponentReference,
)
from gdsfactory.name import clean_name
from gdsfactory.serialization import clean_dict, clean_value_json
from gdsfactory.typings import LayerSpec


def nets_to_connections(
    nets: list[dict[str, Any]], connections: dict[str, Any]
) -> dict[str, str]:
    # Use the given connections; create a shallow copy to avoid mutating the input.
    connections = dict(connections)

    # Flat set of all used ports for O(1) membership check.
    used = set(connections.keys())
    used.update(connections.values())

    for net in nets:
        p = net["p1"]
        q = net["p2"]
        if p in used:
            # Find the already connected q (if any)
            _q = (
                connections[p]
                if p in connections
                else next(k for k, v in connections.items() if v == p)
            )
            raise ValueError(
                "SAX currently does not support multiply connected ports. "
                f"Got {p}<->{q} and {p}<->{_q}"
            )
        if q in used:
            _p = (
                connections[q]
                if q in connections
                else next(k for k, v in connections.items() if v == q)
            )
            raise ValueError(
                "SAX currently does not support multiply connected ports. "
                f"Got {p}<->{q} and {_p}<->{q}"
            )
        connections[p] = q
        used.add(p)
        used.add(q)
    return connections


def get_default_connection_validators() -> dict[str, Callable[..., None]]:
    return {"optical": validate_optical_connection, "electrical": _null_validator}


def get_instance_name_from_alias(reference: ComponentReference) -> str:
    """Returns the instance name from the label.

    If no label returns to instanceName_x_y.

    Args:
        reference: reference that needs naming.
    """
    name = reference.name or md5(str(reference).encode()).hexdigest()[:8]

    return clean_name(name)


def get_instance_name_from_label(
    component: Component,
    reference: ComponentReference,
    layer_label: LayerSpec = "LABEL_INSTANCE",
) -> str:
    """Returns the instance name from the label.

    If no label returns to instanceName_x_y.

    Args:
        component: with labels.
        reference: reference that needs naming.
        layer_label: ignores layer_label[1].
    """
    from gdsfactory.pdk import get_layer

    layer_label = get_layer(layer_label)
    layer = layer_label[0] if isinstance(layer_label, LayerEnum) else layer_label

    x = reference.x
    y = reference.y
    labels = component.labels

    # default instance name follows component.aliases
    text = clean_name(f"{reference.cell.name}_{x}_{y}")

    # try to get the instance name from a label
    for label in labels:
        xl = label.dposition[0]
        yl = label.dposition[1]
        if x == xl and y == yl and label.layer == layer:
            # print(label.text, xl, yl, x, y)
            return str(label.text)

    return text


def _is_array_reference(ref: DInstance | VInstance) -> bool:
    # Direct attribute access is much faster than hasattr(),
    # and in the common case (attributes present) the try branch is very fast.
    try:
        return ref.na > 1 or ref.nb > 1
    except AttributeError:
        return False


def _is_orthogonal_array_reference(ref: ComponentReference) -> bool:
    # Store intermediate attributes to local variables for faster lookup
    a, b = ref.a, ref.b
    ay = a.y
    if abs(ay) != 0:
        return False
    bx = b.x
    return abs(bx) == 0


def _has_ports_on_same_location(reference: VInstance | DInstance) -> bool:
    """Check if a reference has any ports on the same location.

    Args:
        reference: ComponentReference to check.

    Returns:
        True if any ports are on the same location, False otherwise.
    """
    if _is_array_reference(reference):
        # For array references, check each instance
        for ia in range(reference.na):
            for ib in range(reference.nb):
                port_locations = set()
                for port in reference.cell.ports:
                    ref_port = reference.ports[port.name, ia, ib]
                    port_loc = ref_port.to_itype().center
                    if port_loc in port_locations:
                        return True
                    port_locations.add(port_loc)
    else:
        # For single references, check all ports
        port_locations = set()
        for port in reference.ports:
            port_loc = port.to_itype().center
            if port_loc in port_locations:
                return True
            port_locations.add(port_loc)
    return False


def get_netlist(
    component: ProtoTKCell[Any] | VKCell | TKCell,
    exclude_port_types: Sequence[str] | None = ("placement", "pad", "bump"),
    get_instance_name: Callable[..., str] = get_instance_name_from_alias,
    allow_multiple: bool = True,
    connection_error_types: dict[str, list[str]] | None = None,
    add_interface_on_mismatch: bool = False,
    ignore_warnings: bool = False,
) -> dict[str, Any]:
    """From Component returns a dict with instances, connections and placements.

    warnings collected during netlisting are reported back into the netlist.
    These include warnings about mismatched port widths, orientations, shear angles, excessive offsets, etc.
    You can also configure warning types which should throw an error when encountered
    by modifying connection_error_types.
    A key difference in this algorithm is that we group each port type independently.
    This allows us to use different logic to determine i.e.
    if an electrical port is properly connected vs an optical port.
    In this function, the core logic is the same, but we employ extra validation for optical ports.

    Args:
        component: to extract netlist.
        exclude_port_types: optional list of port types to exclude from netlisting.
        get_instance_name: function to get instance name.
        allow_multiple: False to raise an error if more than two ports share the same connection. \
                if True, will return key: [value] pairs with [value] a list of all connected instances.
        connection_error_types: optional dictionary of port types and error types to raise an error for.
        add_interface_on_mismatch: when True, additional interface instances are added to the netlist (e.g. to model mode mismatch)
        ignore_warnings: if True, will not include warnings in the returned netlist.

    Returns:
        instances: Dict of instance name and settings.
        nets: List of connected port pairs/groups
        placements: Dict of instance names and placements (x, y, rotation).
        port: Dict portName: ComponentName,port.
        name: name of component.
        warnings: warning messages (disconnected pins).

    """
    if isinstance(component, VKCell):
        component_: Component | ComponentAllAngle = ComponentAllAngle(
            base=component.base
        )
    elif isinstance(component, ProtoTKCell):
        component_ = Component(base=component.base)
    else:
        component_ = Component(base=component)

    placements: dict[str, dict[str, Any]] = {}
    instances: dict[str, dict[str, Any]] = {}
    nets: list[dict[str, Any]] = []
    top_ports: dict[str, str] = {}

    # store where ports are located
    name2port: dict[str, typings.Port] = {}

    # TOP level ports
    ports = component_.ports
    ports_by_type: defaultdict[str, list[str]] = defaultdict(list)
    top_ports_list: set[str] = set()

    if isinstance(component_, ProtoTKCell):
        references: list[DInstance | VInstance] | list[VInstance] = (
            _get_references_to_netlist(component_)
        )
    else:
        references = _get_references_to_netlist_all_angle(component_)

    for reference in references:
        # Skip references with ports on the same location
        if _has_ports_on_same_location(reference):
            continue

        c = reference.cell
        origin = reference.dcplx_trans.disp
        x = origin.x
        y = origin.y
        reference_name = get_instance_name(reference)
        instance: dict[str, Any] = {}

        if c.info:
            instance.update(component=c.name, info=c.info.model_dump())

        # Don't extract netlist for cells with no function_name (e.g. subcells imported from GDS)
        component_name: str
        if c.function_name:
            component_name = c.function_name
        else:
            if c.name is None:
                component_name = "unnamed_component"
                warn(
                    "Component has no name or function_name. "
                    "Using 'unnamed_component' as default.",
                    stacklevel=2,
                )
            else:
                component_name = c.name
                warn(
                    f"Component {c.name} has no function_name. "
                    "Using component.name instead.",
                    stacklevel=2,
                )

        # Prefer name from settings over c.name
        if c.settings:
            settings = c.settings.model_dump()

            instance.update(
                component=component_name,
                settings=settings,
            )

        instances[reference_name] = instance

        placements[reference_name] = {
            "x": x,
            "y": y,
            "rotation": reference.dcplx_trans.angle,
            "mirror": reference.dcplx_trans.mirror,
        }

        if _is_array_reference(reference):
            if _is_orthogonal_array_reference(reference):  # type: ignore[arg-type]
                instances[reference_name]["array"] = {
                    "columns": reference.na,
                    "rows": reference.nb,
                    "column_pitch": reference.instance.da.x,  # type: ignore[union-attr]
                    "row_pitch": reference.instance.db.y,  # type: ignore[union-attr]
                }
            else:
                instances[reference_name]["array"] = {
                    "num_a": reference.na,
                    "num_b": reference.nb,
                    "pitch_a": (reference.instance.da.x, reference.instance.da.y),  # type: ignore[union-attr]
                    "pitch_b": (reference.instance.db.x, reference.instance.db.y),  # type: ignore[union-attr]
                }
            reference_name = get_instance_name(reference)
            for ia in range(reference.na):
                for ib in range(reference.nb):
                    for port in reference.cell.ports:
                        ref_port = reference.ports[port.name, ia, ib]
                        src = f"{reference_name}<{ia}.{ib}>,{port.name}"
                        name2port[src] = ref_port
                        ports_by_type[port.port_type].append(src)
        else:
            # lower level ports
            for port_ in reference.ports:
                reference_name = get_instance_name(reference)
                src = f"{reference_name},{port_.name}"
                name2port[src] = port_
                ports_by_type[port_.port_type].append(src)

    for port in ports:
        port_name = port.name
        if port_name is not None:
            name2port[port_name] = port
            top_ports_list.add(port_name)
            ports_by_type[port.port_type].append(port_name)

    warnings: dict[str, Any] = {}
    for port_type, port_names in ports_by_type.items():
        if exclude_port_types and port_type in exclude_port_types:
            continue
        connections_t, warnings_t = extract_connections(
            port_names,
            name2port,
            port_type,
            allow_multiple=allow_multiple,
            connection_error_types=connection_error_types,
        )
        if warnings_t and not ignore_warnings:
            warnings[port_type] = warnings_t
        for connection in connections_t:
            if len(connection) == 2:
                src, dst = connection
                if src in top_ports_list:
                    top_ports[src] = dst
                elif dst in top_ports_list:
                    top_ports[dst] = src
                else:
                    if add_interface_on_mismatch:
                        insert_interface_if_needed(
                            src=src,
                            dst=dst,
                            instances=instances,
                            placements=placements,
                            nets=nets,
                            name2port=name2port,
                        )
                    else:
                        src_dest = sorted([src, dst])
                        net = {"p1": src_dest[0], "p2": src_dest[1]}
                        nets.append(net)

    # sort nets by p1 (and then p2, in the case of a tie)
    nets_sorted = sorted(nets, key=lambda net: f"{net['p1']},{net['p2']}")
    placements_sorted = {k: placements[k] for k in sorted(placements.keys())}
    instances_sorted = {k: instances[k] for k in sorted(instances.keys())}
    netlist: dict[str, Any] = {
        "nets": nets_sorted,
        "instances": instances_sorted,
        "placements": placements_sorted,
        "ports": top_ports,
        "name": component_.name,
    }
    if warnings:
        netlist["warnings"] = warnings
    return clean_value_json(netlist)  # type: ignore[no-any-return]


def insert_interface_if_needed(
    src: str,
    dst: str,
    instances: dict[str, dict[str, Any]],
    placements: dict[str, dict[str, Any]],
    nets: list[dict[str, Any]],
    name2port: dict[str, typings.Port],
) -> None:
    # check cross sections for equality
    src_xs_name = name2port[src].info.get("cross_section")
    dst_xs_name = name2port[dst].info.get("cross_section")
    xs_mismatch = src_xs_name != dst_xs_name

    # check port radii for (signed) equality
    src_r = name2port[src].info.get("radius")
    dst_r = name2port[dst].info.get("radius")
    # mirroring an instance turns left bends into right bends and vice versa
    if placements[src.split(",")[0]]["mirror"] and src_r is not None:
        src_r = -src_r
    if placements[dst.split(",")[0]]["mirror"] and dst_r is not None:
        dst_r = -dst_r
    # Considering signal from src to dst, src_r stays outward oriented
    # and dst_r must be turned from outward to inward orientation (inverted).
    dst_r = dst_r if dst_r is None else -dst_r
    r_mismatch = src_r != dst_r

    if xs_mismatch or r_mismatch:  # inject interface instance and reconnect ports
        intf_name = f"interface__{src.replace(',', '_')}__{dst.replace(',', '_')}"
        if intf_name in instances:
            raise ValueError(f"'{intf_name}' already present in instances.")
        settings = {
            "width1": name2port[src].cross_section.width,
            "width2": name2port[dst].cross_section.width,
            "radius1": src_r,
            "radius2": dst_r,
            "cross_section1": src_xs_name,
            "cross_section2": dst_xs_name,
        }
        instances[intf_name] = {"component": "interface", "settings": settings}
        src1, dst1 = sorted([src, f"{intf_name},o1"])
        src2, dst2 = sorted([dst, f"{intf_name},o2"])
        nets.extend([{"p1": src1, "p2": dst1}, {"p1": src2, "p2": dst2}])
    else:  # just do normal connection for matched ports
        src_dest = sorted([src, dst])
        net = {"p1": src_dest[0], "p2": src_dest[1]}
        nets.append(net)


def extract_connections(
    port_names: Sequence[str],
    ports: dict[str, typings.Port],
    port_type: str,
    validators: dict[str, Callable[..., None]] | None = None,
    allow_multiple: bool = True,
    connection_error_types: dict[str, list[str]] | None = None,
) -> tuple[list[list[str]], dict[str, list[dict[str, Any]]]]:
    if validators is None:
        validators = DEFAULT_CONNECTION_VALIDATORS

    validator = validators.get(port_type, _null_validator)
    return _extract_connections(
        port_names,
        ports,
        port_type,
        connection_validator=validator,
        allow_multiple=allow_multiple,
        connection_error_types=connection_error_types,
    )


def _extract_connections(
    port_names: Sequence[str],
    ports: dict[str, typings.Port],
    port_type: str,
    connection_validator: Callable[..., None],
    raise_error_for_warnings: list[str] | None = None,
    allow_multiple: bool = True,
    connection_error_types: dict[str, list[str]] | None = None,
) -> tuple[list[list[str]], dict[str, list[Any]]]:
    """Extracts connections between ports.

    Args:
        port_names: list of port names.
        ports: dict of port names to Port objects.
        port_type: type of port.
        connection_validator: function to validate connections.
        raise_error_for_warnings: list of warning types to raise an error for.
        allow_multiple: False to raise an error if more than two ports share the same connection.
        connection_error_types: optional dictionary of port types and error types to raise an error for.

    """
    if connection_error_types is None:
        connection_error_types = DEFAULT_CRITICAL_CONNECTION_ERROR_TYPES

    warnings: defaultdict[str, list[Any]] = defaultdict(list)
    if raise_error_for_warnings is None:
        raise_error_for_warnings = connection_error_types.get(port_type, [])

    unconnected_port_names: list[str] = list(port_names)
    connections: list[list[str]] = []

    by_xy: dict[tuple[float, float], list[str]] = defaultdict(list)

    for port_name in unconnected_port_names:
        port = ports[port_name]
        by_xy[port.to_itype().center].append(port_name)

    unconnected_port_names = []

    for xy, ports_at_xy in by_xy.items():
        if len(ports_at_xy) == 1:
            unconnected_port_names.append(ports_at_xy[0])

        elif len(ports_at_xy) == 2:
            port1 = ports[ports_at_xy[0]]
            port2 = ports[ports_at_xy[1]]
            connection_validator(port1, port2, ports_at_xy, warnings)
            connections.append(ports_at_xy)

        elif not allow_multiple:
            warnings["multiple_connections"].append(ports_at_xy)
            warn(f"Found multiple connections at {xy}:{ports_at_xy}", stacklevel=3)

        else:
            # Iterates over the list of multiple ports to create related two-port connectivity
            num_ports = len(ports_at_xy)
            for portindex1, portindex2 in zip(
                range(-1, num_ports - 1), range(num_ports), strict=False
            ):
                port1 = ports[ports_at_xy[portindex1]]
                port2 = ports[ports_at_xy[portindex2]]
                connection_validator(port1, port2, ports_at_xy, warnings)
                connections.append([ports_at_xy[portindex1], ports_at_xy[portindex2]])

    if unconnected_port_names:
        unconnected_non_top_level = [
            pname for pname in unconnected_port_names if ("," in pname)
        ]
        if unconnected_non_top_level:
            unconnected_xys = [
                ports[pname].center for pname in unconnected_non_top_level
            ]
            warnings["unconnected_ports"].append(
                _make_warning(
                    ports=unconnected_non_top_level,
                    values=unconnected_xys,
                    message=f"{len(unconnected_non_top_level)} unconnected {port_type} ports!",
                )
            )

    critical_warnings = {
        w: warnings[w] for w in raise_error_for_warnings if w in warnings
    }

    if critical_warnings and raise_error_for_warnings:
        pprint(critical_warnings)
        warn("Found critical warnings while extracting netlist", stacklevel=3)
    return connections, dict(warnings)


def _make_warning(ports: list[str], values: Any, message: str) -> dict[str, Any]:
    w = {
        "ports": ports,
        "values": values,
        "message": message,
    }
    return clean_dict(w)


def _null_validator(
    port1: Port,
    port2: Port,
    port_names: list[str],
    warnings: dict[str, list[dict[str, Any]]],
) -> None:
    pass


def validate_optical_connection(
    port1: Port,
    port2: Port,
    port_names: list[str],
    warnings: dict[str, list[dict[str, Any]]],
    angle_tolerance: float = 0.01,
    offset_tolerance: float = 0.001,
    width_tolerance: float = 0.001,
) -> None:
    is_top_level = [("," not in pname) for pname in port_names]

    if len(port_names) != 2:
        raise ValueError(
            f"More than two connected optical ports: {port_names} at {port1.center}"
        )

    if all(is_top_level):
        raise ValueError(f"Two top-level ports appear to be connected: {port_names}")

    if abs(port1.width - port2.width) > width_tolerance:
        warnings["width_mismatch"].append(
            _make_warning(
                port_names,
                values=[port1.width, port2.width],
                message=f"Widths of ports {port_names[0]} and {port_names[1]} not equal. "
                f"Difference of {abs(port1.width - port2.width)} um",
            )
        )

    if any(is_top_level):
        if (
            abs(difference_between_angles(port1.orientation, port2.orientation))
            > angle_tolerance
        ):
            top_port, lower_port = port_names if is_top_level[0] else port_names[::-1]
            warnings["orientation_mismatch"].append(
                _make_warning(
                    port_names,
                    values=[port1.orientation, port2.orientation],
                    message=f"{lower_port} was promoted to {top_port} but orientations"
                    f"do not match! Difference of {(abs(port1.orientation - port2.orientation))} deg",
                )
            )
    else:
        angle_misalignment = abs(
            abs(difference_between_angles(port1.orientation, port2.orientation)) - 180
        )
        if angle_misalignment > angle_tolerance:
            warnings["orientation_mismatch"].append(
                _make_warning(
                    port_names,
                    values=[port1.orientation, port2.orientation],
                    message=f"{port_names[0]} and {port_names[1]} are misaligned by {angle_misalignment} deg",
                )
            )

    offset_mismatch = np.sqrt(np.sum(np.square(np.array(port2.center) - port1.center)))
    if offset_mismatch > offset_tolerance:
        warnings["offset_mismatch"].append(
            _make_warning(
                port_names,
                values=[port1.center, port2.center],
                message=f"{port_names[0]} and {port_names[1]} are offset by {offset_mismatch} um",
            )
        )


def difference_between_angles(angle2: float, angle1: float) -> float:
    diff = angle2 - angle1
    while diff < 180:
        diff += 360
    while diff > 180:
        diff -= 360
    return diff


def _get_references_to_netlist(component: Component) -> list[DInstance | VInstance]:
    insts = component.insts
    vinsts = component.vinsts
    return list(insts) + list(vinsts)


def _get_references_to_netlist_all_angle(
    component: ComponentAllAngle,
) -> list[VInstance]:
    insts = list(component.insts)
    return insts


class GetNetlistFunc(Protocol):
    def __call__(self, component: AnyKCell, **kwargs: Any) -> dict[str, Any]: ...


def get_netlist_recursive(
    component: AnyKCell,
    component_suffix: str = "",
    get_netlist_func: GetNetlistFunc = get_netlist,  # type: ignore[assignment]
    get_instance_name: Callable[..., str] = get_instance_name_from_alias,
    **kwargs: Any,
) -> dict[str, Any]:
    """Returns recursive netlist for a component and subcomponents.

    Args:
        component: to extract netlist.
        component_suffix: suffix to append to each component name.
            useful if to save and reload a back-annotated netlist.
        get_netlist_func: function to extract individual netlists.
        get_instance_name: function to get instance name.
        kwargs: additional keyword arguments to pass to get_netlist_func.

    Keyword Args:
        tolerance: tolerance in grid_factor to consider two ports connected.
        exclude_port_types: optional list of port types to exclude from netlisting.
        get_instance_name: function to get instance name.

    Returns:
        Dictionary of netlists, keyed by the name of each component.

    """
    all_netlists: dict[str, Any] = {}

    # only components with references (subcomponents) warrant a netlist
    if isinstance(component, ProtoTKCell):
        component = Component(base=component.base)
        references: list[DInstance | VInstance] | list[VInstance] = (
            _get_references_to_netlist(component)
        )
    else:
        component = ComponentAllAngle(base=component.base)
        references = _get_references_to_netlist_all_angle(component)

    if references:
        netlist = get_netlist_func(component, **kwargs)
        all_netlists[f"{component.name}{component_suffix}"] = netlist

        # for each reference, expand the netlist
        for ref in references:
            rcell = ref.cell
            grandchildren = get_netlist_recursive(
                component=rcell,
                component_suffix=component_suffix,
                get_netlist_func=get_netlist_func,
                **kwargs,
            )
            all_netlists |= grandchildren

            if isinstance(ref.cell, ProtoTKCell):
                child_references: list[VInstance | DInstance] | list[VInstance] = (
                    _get_references_to_netlist(Component(base=ref.cell.base))
                )
            else:
                child_references = _get_references_to_netlist_all_angle(
                    ComponentAllAngle(base=ref.cell)  # type: ignore[call-overload]
                )

            if child_references:
                inst_name = get_instance_name(ref)
                netlist_dict: dict[str, Any] = {
                    "component": f"{rcell.name}{component_suffix}"
                }
                if hasattr(rcell, "settings"):
                    netlist_dict.update(settings=rcell.settings.model_dump())
                if hasattr(rcell, "info"):
                    netlist_dict.update(info=rcell.info.model_dump())
                netlist["instances"][inst_name] = netlist_dict

    return all_netlists


def _demo_ring_single_array() -> None:
    from gdsfactory.components.rings.ring_single_array import ring_single_array

    c = ring_single_array()
    c.get_netlist()


def _demo_mzi_lattice() -> None:
    import gdsfactory as gf

    coupler_lengths = [10, 20, 30, 40]
    coupler_gaps = [0.1, 0.2, 0.4, 0.5]
    delta_lengths = [10, 100, 200]

    c = gf.components.mzi_lattice(
        coupler_lengths=coupler_lengths,
        coupler_gaps=coupler_gaps,
        delta_lengths=delta_lengths,
    )
    c.get_netlist()


DEFAULT_CONNECTION_VALIDATORS = get_default_connection_validators()

DEFAULT_CRITICAL_CONNECTION_ERROR_TYPES = {
    "optical": ["width_mismatch", "shear_angle_mismatch", "orientation_mismatch"]
}
