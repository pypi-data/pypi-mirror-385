from netbox_network_importer.connections.Netbox import Netbox
from netbox_network_importer.helper import canonical_interface_name_edited, get_diff
from netbox_network_importer.helpers.result_factory import NetboxResultFactory
from netbox_network_importer.results.results import Action, NetboxResult, Status


def process_interfaces(host, parsed_interfaces) -> list:
    """CRUD on netbox interfaces
    - Delete interfaces, that exists in netbox but are not passed from device
    - Update interfaces, which already exists in netbox
    - Create interfaces, which does not exists in netbox

    :param parsed_interfaces: parsed interfaces for netbox operations
    :param host: host of the task (netbox device representation)

    :returns: list of NetboxResult
    """

    RESULTS = []  # list of NetboxResult

    # Init connection to Netbox via PyNetbox
    nb = Netbox.connect()

    # find the device instance in netbox
    dev = nb.dcim.devices.get(host.data["id"])

    # find interfaces linked to the device
    ifcs_filter = nb.dcim.interfaces.filter(device_id=dev.id)

    # convert filtered interfaces into dictionary of pynetbox interface instances
    nb_interfaces_dict = {
        canonical_interface_name_edited(ifc.name): ifc
        for ifc in [ifc for ifc in ifcs_filter]
    }

    # setup NB parameters
    for ifc, properties in parsed_interfaces.items():
        mac_address = properties.get("mac_address")
        ifc_params = {
            "name": ifc,
            "enabled": properties["enabled"],
            "description": properties["description"].strip(),
            "type": properties["type"],
            "mtu": properties["mtu"],
        }

        # get NB interface instance
        nb_ifc = nb_interfaces_dict.get(ifc, None)

        if nb_ifc:
            # Skip IGNORED interfaces
            if nb_ifc.custom_fields.get("ignore_importer") is True:
                RESULTS.append(
                    NetboxResult(
                        result=f"{nb_ifc.name} - Ignored by Importer - Skipping",
                        status=Status.SKIPPED,
                        action=Action.LOOKUP,
                        diff="",
                    )
                )

                nb_interfaces_dict.pop(nb_ifc.name, None)
                continue
            else:
                # If interface already exists in netbox, update it
                RESULTS.append(interface_update(nb_ifc=nb_ifc, params=ifc_params))
                # For MAC address processing, we can use the existing nb_ifc object
        else:
            # Otherwise, create it
            ifc_params["device"] = {"id": dev.id}
            RESULTS.append(interface_create(ifc_params=ifc_params, nb=nb))
            # After creating, fetch the fresh object for MAC address processing
            nb_ifc = nb.dcim.interfaces.get(name=ifc, device_id=dev.id)

        # Process MAC address (nb_ifc is now available from either update or create path)
        if nb_ifc:
            if nb_ifc.primary_mac_address:
                RESULTS.append(mac_address_update(nb_ifc, mac_address))
            else:
                RESULTS.append(mac_address_create(nb_ifc, mac_address, nb))

        # Pop device from dictionary if it's updated / created
        nb_interfaces_dict.pop(ifc, None)

    # If any interface is left in `nb_interfaces_dict`, then it should be removed from netbox
    #   - Interface exists in netbox, but the interface was not passed from network
    for ifc_name, nb_ifc in nb_interfaces_dict.items():
        RESULTS.append(interface_delete(ifc=nb_ifc))

    return RESULTS


def interface_delete(ifc):
    from netbox_network_importer.helpers import (
        NetboxResultFactory,
        create_cable_check_result,
        handle_netbox_operation,
        should_skip_interface,
    )

    # Check for cable connection
    if ifc.cable:
        return create_cable_check_result(ifc.name, ifc)

    # Check if interface should be ignored
    if should_skip_interface(ifc):
        return NetboxResultFactory.create_check_manually(
            name=ifc.name,
            reason="Interface Ignored",
            action=Action.DELETE,
            diff={
                "name": ifc.name,
                "device_name": ifc.device.name,
                "description": ifc.description,
                "ignore_importer": ifc.custom_fields.get("ignore_importer", False),
            },
        )

    # Use the error handling decorator for the actual deletion
    @handle_netbox_operation("Interface deletion", Action.DELETE)
    def _delete_interface(interface):
        if interface.delete():
            return NetboxResultFactory.create_success(
                name=interface.name,
                action=Action.DELETE,
                diff={
                    "name": interface.name,
                    "device": interface.device.name,
                    "description": interface.description,
                },
            )
        else:
            return NetboxResult(
                result=f"{interface.name} - could not be deleted",
                status=Status.ANOMALLY,
                action=Action.DELETE,
                diff={},
            )

    return _delete_interface(ifc)


def mac_address_update(nb_ifc, mac_address):
    # Handle MAC address separately since it's now a separate model
    if mac_address:
        # Create MAC address object if it doesn't exist
        mac_addr_obj = nb_ifc.primary_mac_address
        before = str(mac_addr_obj.mac_address)

        if mac_addr_obj.mac_address != mac_address:
            mac_addr_obj.mac_address = mac_address
            nb_ifc.primary_mac_address = mac_addr_obj
            mac_addr_obj.save()
            nb_ifc.save()

            return NetboxResultFactory.create_success(
                name=nb_ifc.name,
                action=Action.UPDATE,
                diff=get_diff(before, mac_address),
                message=f"{nb_ifc.name} - MAC address updated successfully",
            )
        else:
            return NetboxResultFactory.create_no_change(
                name=nb_ifc.name,
                action=Action.UPDATE,
                message=f"{nb_ifc.name} - MAC address already exists",
            )
    else:
        return NetboxResult(
            result=f"{nb_ifc.name} - MAC address not provided",
            status=Status.NOT_CHANGED,
            action=Action.UPDATE,
            diff={},
        )


def mac_address_create(nb_ifc, mac_address, nb):
    from loguru import logger
    from pynetbox.core.query import RequestError

    if mac_address:
        try:
            mac_addr_obj = nb.dcim.mac_addresses.create(
                assigned_object_id=nb_ifc.id,
                assigned_object_type="dcim.interface",
                mac_address=mac_address,
            )
            nb_ifc.primary_mac_address = mac_addr_obj
            nb_ifc.save()
            return NetboxResult(
                result=f"{nb_ifc.name} - MAC address created successfully",
                status=Status.CHANGED,
                action=Action.CREATE,
                diff={"mac_address": mac_address},
            )
        except RequestError as e:
            logger.error(
                f"MAC address creation failed for interface {nb_ifc.name} (NetBox ID: {nb_ifc.id}) - {str(e)}"
            )
            return NetboxResult(
                result=f"{nb_ifc.name} - MAC address could not be created: {str(e)}",
                status=Status.FAILED,
                action=Action.CREATE,
                diff={},
                exception=e,
            )
        except Exception as e:
            logger.error(
                f"MAC address creation exception for interface {nb_ifc.name} (NetBox ID: {nb_ifc.id}) - {str(e)}"
            )
            return NetboxResult(
                result=f"{nb_ifc.name} - MAC address could not be created: {str(e)}",
                status=Status.EXCEPTION,
                action=Action.CREATE,
                diff={},
                exception=e,
            )
    else:
        return NetboxResult(
            result=f"{nb_ifc.name} - MAC address not provided",
            status=Status.NOT_CHANGED,
            action=Action.CREATE,
            diff={},
        )


def interface_update(nb_ifc, params):
    from loguru import logger
    from pynetbox.core.query import RequestError

    try:
        # Get data before changes
        before = get_changed_params(nb_ifc)

        # TODO: Don't change ifc type if Other -
        if params.get("type", None) == "other":
            params.pop("type")

        if nb_ifc.update(params):
            # TODO: Reload ifc
            nb_ifc = nb_ifc.api.dcim.interfaces.get(nb_ifc.id)
            after = get_changed_params(nb_ifc)

            return NetboxResult(
                result=f"{nb_ifc.name} - saved successfully",
                status=Status.CHANGED,
                action=Action.UPDATE,
                diff=get_diff(before, after),
            )
        else:
            return NetboxResult(
                result=f"{nb_ifc.name} - nothing to do",
                action=Action.UPDATE,
                status=Status.NOT_CHANGED,
                diff={},
            )
    except RequestError as e:
        logger.error(
            f"Interface update failed: {nb_ifc.name} (NetBox ID: {nb_ifc.id}) - {str(e)}"
        )
        return NetboxResult(
            result=f"{nb_ifc.name} - could not be updated: {str(e)}",
            status=Status.FAILED,
            action=Action.UPDATE,
            diff={},
            exception=e,
        )
    except Exception as e:
        return NetboxResult(
            result=f"{nb_ifc.name} - Exception Occurs: {e}",
            status=Status.EXCEPTION,
            action=Action.UPDATE,
            diff={},
            exception=e,
        )


def interface_create(ifc_params, nb):
    from loguru import logger
    from pynetbox.core.query import RequestError

    try:
        netbox_interface = nb.dcim.interfaces.create(ifc_params)

        if netbox_interface:
            return NetboxResult(
                result=f"{netbox_interface.name} - created successfully",
                status=Status.CHANGED,
                action=Action.CREATE,
                diff=ifc_params,
            )
        else:
            return NetboxResult(
                result=f"{ifc_params['name']} - ERROR!",
                status=Status.FAILED,
                action=Action.CREATE,
                diff={},
            )
    except RequestError as e:
        logger.error(f"Interface creation failed: {ifc_params['name']} - {str(e)}")
        return NetboxResult(
            result=f"{ifc_params['name']} - could not be created: {str(e)}",
            status=Status.FAILED,
            action=Action.CREATE,
            diff={},
            exception=e,
        )
    except Exception as e:
        return NetboxResult(
            result=f"{ifc_params['name']} - Exception Occurs: {e}",
            status=Status.EXCEPTION,
            action=Action.CREATE,
            diff={},
            exception=e,
        )


def get_changed_params(nb_interface):
    return {
        "name": nb_interface.name,
        "enabled": nb_interface.enabled,
        "description": nb_interface.description,
        "type": nb_interface.type,
        "mtu": nb_interface.mtu,
        "mac_address": nb_interface.mac_address,
    }
