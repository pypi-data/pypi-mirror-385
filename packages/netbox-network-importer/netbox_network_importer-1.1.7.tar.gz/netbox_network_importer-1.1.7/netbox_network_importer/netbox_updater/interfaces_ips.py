from netbox_network_importer.connections.Netbox import Netbox
from netbox_network_importer.helpers import (
    NetboxBatchQuery,
    NetboxResultFactory,
    create_ignored_interface_result,
    handle_netbox_operation,
    should_skip_interface,
)
from netbox_network_importer.results.results import Action


def process_interfaces_ips(host, parsed_interfaces) -> list:
    """CRUD on netbox interfaces IPs
    - Delete IPs, that exists in netbox but are not passed from device
    - Update IPs, which already exists in netbox
    - Create IPs, which does not exists in netbox

    :param parsed_interfaces: parsed interfaces for netbox operations
    """

    # Init connection to Netbox via PyNetbox
    nb = Netbox.connect()

    RESULTS = []

    # find the device instance in netbox
    dev = nb.dcim.devices.get(host.data["id"])

    # Use batch query for better performance
    batch_query = NetboxBatchQuery(nb)
    nb_interfaces_dict = batch_query.get_device_interfaces(dev.id)
    device_ips_by_interface = batch_query.get_device_ip_addresses(dev.id)

    # Create DICT of ALL
    #    = parsed interfaces from genie (that with IP address assigned)
    #    = all interfaces stored in netbox (if not parsed with genie, empty dict of ip addresses passed)
    ALL_INTERFACES = {}
    ALL_INTERFACES.update({k: {} for k in nb_interfaces_dict})
    ALL_INTERFACES.update(parsed_interfaces)

    # Loop over all interfaces and process their IP addreses (CRUD)
    for ifc, parsed_ips in ALL_INTERFACES.items():
        # get NB interface instance
        nb_ifc = nb_interfaces_dict.get(ifc, None)
        # get NB interface ip addresses and convert to dictionary
        if nb_ifc is None:
            RESULTS.append(
                NetboxResultFactory.create_not_found(
                    name=f"Interface {ifc}",
                    context=f"Configured IPS: {parsed_ips} - Check manually",
                    action=Action.LOOKUP,
                )
            )
            continue

        # Skip IGNORED interfaces
        if should_skip_interface(nb_ifc):
            RESULTS.append(create_ignored_interface_result(nb_ifc.name, Action.LOOKUP))
            continue

        # Get IP addresses for this interface from the batch-loaded data
        nb_interface_ips_dict = device_ips_by_interface.get(nb_ifc.id, {})

        # Go through different family addresses
        for address_family in parsed_ips:
            if address_family == "ipv4":
                family = {"value": 4, "label": "IPv4"}
                default_prefix = 32
            elif address_family == "ipv6":
                family = {"value": 6, "label": "IPv6"}
                default_prefix = 128

            for ip, props in parsed_ips[address_family].items():
                # TODO:
                if ip == "0.0.0.0":
                    continue

                prefix = props.get("prefix_length", default_prefix)
                ip = f"{ip}/{prefix}"

                # Pop device from dictionary - if none, create it
                if not nb_interface_ips_dict.pop(ip, None):
                    ip_params = {
                        "assigned_object_type": "dcim.interface",
                        "assigned_object_id": nb_ifc.id,
                        "family": family,
                        "address": ip,
                    }
                    RESULTS.append(
                        ip_create(ip_params=ip_params, nb=nb, ifc_name=nb_ifc.name)
                    )

        # If any IP is left in `nb_interface_ips_dict`, then it should be removed from netbox
        #   - IP exists in netbox, but the IP was not passed from network
        for _k, nb_ip_address in nb_interface_ips_dict.items():
            RESULTS.append(ip_delete(ip=nb_ip_address, ifc_name=nb_ifc.name))

    return RESULTS


def ip_delete(ip, ifc_name):
    @handle_netbox_operation("IP address deletion", Action.DELETE)
    def _delete_ip(ip_obj, interface_name):
        if ip_obj.delete():
            return NetboxResultFactory.create_success(
                name=f"{interface_name} - {ip_obj.address}",
                action=Action.DELETE,
                diff={},
            )
        else:
            return NetboxResultFactory.create_failed(
                name=f"{interface_name} - {ip_obj.address}",
                error="could not be deleted",
                action=Action.DELETE,
            )

    return _delete_ip(ip, ifc_name)


def ip_create(ip_params, nb, ifc_name):
    @handle_netbox_operation("IP address creation", Action.CREATE)
    def _create_ip(params, netbox_conn, interface_name):
        netbox_ip = netbox_conn.ipam.ip_addresses.create(params)

        if netbox_ip:
            return NetboxResultFactory.create_success(
                name=f"{interface_name} - {netbox_ip.address}",
                action=Action.CREATE,
                diff=params,
            )
        else:
            return NetboxResultFactory.create_failed(
                name=f"{interface_name} - {params['address']}",
                error="Unable to create",
                action=Action.CREATE,
            )

    return _create_ip(ip_params, nb, ifc_name)
