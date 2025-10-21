from netbox_network_importer.connections.Netbox import Netbox
from netbox_network_importer.helpers import (
    NetboxBatchQuery,
    NetboxResultFactory,
    create_ignored_interface_result,
    should_skip_interface,
)
from netbox_network_importer.results.results import Action


def process_bandwidth_interfaces(host, converted_bandwidth_ifcs) -> list:
    RESULTS = []  # list of NetboxResult

    # Init connection to Netbox via PyNetbox
    nb = Netbox.connect()

    # find the device instance in netbox
    dev = nb.dcim.devices.get(host.data["id"])

    # Use batch query for better performance
    batch_query = NetboxBatchQuery(nb)
    nb_interfaces_dict = batch_query.get_device_interfaces(dev.id)

    # setup NB parameters
    for ifc, bandwidth in converted_bandwidth_ifcs.items():
        # get NB interface instance
        nb_ifc = nb_interfaces_dict.get(ifc, None)

        if nb_ifc:
            # Skip IGNORED interfaces
            if should_skip_interface(nb_ifc):
                RESULTS.append(
                    create_ignored_interface_result(nb_ifc.name, Action.LOOKUP)
                )
                continue
            else:
                # If interface already exists in netbox, update it
                RESULTS.append(
                    interface_bandwidth_update(nb_ifc=nb_ifc, bandwidth=bandwidth)
                )
        else:
            RESULTS.append(
                NetboxResultFactory.create_not_found(
                    name=f"Interface {ifc}",
                    context="Bandwidth update",
                    action=Action.LOOKUP,
                )
            )
    return RESULTS


def interface_bandwidth_update(nb_ifc, bandwidth):
    from netbox_network_importer.helpers import handle_netbox_operation

    # Check if update is actually needed
    before = nb_ifc.custom_fields.get("bandwidth", None)
    if before == bandwidth:
        return NetboxResultFactory.create_no_change(nb_ifc.name, Action.UPDATE)

    @handle_netbox_operation("Bandwidth update", Action.UPDATE)
    def _update_bandwidth(interface, new_bandwidth):
        if interface.update({"custom_fields": {"bandwidth": new_bandwidth}}):
            return NetboxResultFactory.create_update_result(
                name=interface.name,
                before=before,
                after=new_bandwidth,
            )
        else:
            return NetboxResultFactory.create_no_change(interface.name, Action.UPDATE)

    return _update_bandwidth(nb_ifc, bandwidth)
