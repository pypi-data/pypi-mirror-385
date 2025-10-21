from netbox_network_importer.connections.Netbox import Netbox
from netbox_network_importer.helper import (
    canonical_interface_name_edited,
    get_netbox_interface_type,
)
from netbox_network_importer.helpers import (
    NetboxBatchQuery,
    NetboxResultFactory,
    create_ignored_interface_result,
    handle_netbox_operation,
    should_skip_interface,
)
from netbox_network_importer.results.results import Action


def process_lag_interfaces(host, parsed_lag_interfaces) -> list:
    """Update netbox lag interfaces
    - Update lag interfaces, which already exists in netbox

    :param parsed_interfaces: parsed interfaces for netbox operations
    """

    RESULTS = []

    # Init connection to Netbox via PyNetbox
    nb = Netbox.connect()

    # find the device instance in netbox
    dev = nb.dcim.devices.get(host.data["id"])

    # Use batch query for better performance
    batch_query = NetboxBatchQuery(nb)
    NB_LAG_INTERFACES_dict = batch_query.get_lag_interfaces(dev.id)
    NB_LAG_CHILDREN_dict = batch_query.get_lag_children(dev.id)

    for parent_lag, children_of_lag in parsed_lag_interfaces.items():
        nb_parent_lag_ifc = NB_LAG_INTERFACES_dict.get(
            canonical_interface_name_edited(parent_lag), None
        )

        # if parent not found in netbox, skip to next record
        if not nb_parent_lag_ifc:
            RESULTS.append(
                NetboxResultFactory.create_not_found(
                    name=f"Parent LAG interface: {parent_lag}",
                    context=f"could not be found in netbox on device: {host.name}",
                    action=Action.LOOKUP,
                )
            )
            continue

        # Skip IGNORED interfaces
        if should_skip_interface(nb_parent_lag_ifc):
            RESULTS.append(
                create_ignored_interface_result(nb_parent_lag_ifc.name, Action.LOOKUP)
            )
            NB_LAG_INTERFACES_dict.pop(nb_parent_lag_ifc.name, None)

        else:
            # SET parent interface as lag
            RESULTS.append(
                interface_parent_update(
                    nb_ifc=nb_parent_lag_ifc, params={"type": "lag"}
                )
            )

            # Pop processed parent of already existing lags
            NB_LAG_INTERFACES_dict.pop(nb_parent_lag_ifc.name, None)

        for lag_child in children_of_lag:
            nb_child_ifc = NB_LAG_CHILDREN_dict.get(
                canonical_interface_name_edited(lag_child), None
            )

            # if child not found in netbox, skip to next record
            if not nb_child_ifc:
                RESULTS.append(
                    NetboxResultFactory.create_not_found(
                        name=f"Child interface {canonical_interface_name_edited(lag_child)}",
                        context=f"could not be found in netbox on device {host.name}",
                        action=Action.LOOKUP,
                    )
                )
                continue

            # Skip IGNORED interfaces
            if should_skip_interface(nb_child_ifc):
                RESULTS.append(
                    create_ignored_interface_result(nb_child_ifc.name, Action.LOOKUP)
                )
                NB_LAG_CHILDREN_dict.pop(nb_child_ifc.name, None)
                continue
            elif should_skip_interface(nb_parent_lag_ifc):
                RESULTS.append(
                    NetboxResultFactory.create_skipped(
                        name=nb_child_ifc.name,
                        reason="PARENT Ignored by Importer",
                        action=Action.LOOKUP,
                    )
                )
                NB_LAG_CHILDREN_dict.pop(nb_child_ifc.name, None)
                continue
            else:
                # set parent to a child interface
                RESULTS.append(
                    interface_child_update(
                        nb_ifc=nb_child_ifc, params={"lag": nb_parent_lag_ifc}
                    )
                )

                # Pop processed child of alredy existing children
                NB_LAG_CHILDREN_dict.pop(nb_child_ifc.name, None)

    # Remove LAG children interfaces that are no longer configured as LAG members
    for ifc_name, nb_ifc in NB_LAG_CHILDREN_dict.items():
        RESULTS.append(interface_child_update(nb_ifc=nb_ifc, params={"lag": None}))

    # Update LAG parent interfaces that are no longer configured as LAGs
    # Note: LAG interfaces without children can still exist and remain as LAG type
    for ifc_name, nb_ifc in NB_LAG_INTERFACES_dict.items():
        RESULTS.append(
            interface_parent_update(
                nb_ifc=nb_ifc, params={"type": get_netbox_interface_type(ifc_name)}
            )
        )

    return RESULTS


def interface_parent_update(nb_ifc, params):
    @handle_netbox_operation("LAG parent interface update", Action.UPDATE)
    def _update_parent(interface, update_params):
        before = get_changes_parent_interface(interface)

        if interface.update(update_params):
            # Reload interface to get updated state from Netbox
            interface = interface.api.dcim.interfaces.get(interface.id)
            after = get_changes_parent_interface(interface)

            return NetboxResultFactory.create_update_result(
                name=f"{interface.name} - LAG",
                before=before,
                after=after,
            )
        else:
            return NetboxResultFactory.create_no_change(
                name=f"{interface.name} - LAG",
                action=Action.UPDATE,
            )

    return _update_parent(nb_ifc, params)


def interface_child_update(nb_ifc, params):
    @handle_netbox_operation("LAG child interface update", Action.UPDATE)
    def _update_child(interface, update_params):
        before = get_changes_child_interface(interface)

        if interface.update(update_params):
            # Reload interface to get updated state from Netbox
            interface = interface.api.dcim.interfaces.get(interface.id)
            after = get_changes_child_interface(interface)

            return NetboxResultFactory.create_update_result(
                name=f"{interface.name} - LAG Parent",
                before=before,
                after=after,
            )
        else:
            return NetboxResultFactory.create_no_change(
                name=interface.name,
                action=Action.UPDATE,
            )

    return _update_child(nb_ifc, params)


def get_changes_parent_interface(nb_ifc):
    return {"type": nb_ifc.type.label}


def get_changes_child_interface(nb_ifc):
    if nb_ifc.lag:
        return {"lag": nb_ifc.lag.name}
    else:
        return {"lag": None}
