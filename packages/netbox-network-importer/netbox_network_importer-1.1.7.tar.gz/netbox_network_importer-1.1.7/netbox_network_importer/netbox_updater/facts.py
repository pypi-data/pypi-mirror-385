import datetime

from netbox_network_importer.connections.Netbox import Netbox
from netbox_network_importer.helper import get_diff
from netbox_network_importer.helpers.error_handling import handle_netbox_operation
from netbox_network_importer.helpers.result_factory import NetboxResultFactory
from netbox_network_importer.results.results import Action


@handle_netbox_operation("Device facts update", Action.UPDATE)
def process_facts(host, napalm_facts) -> list:
    RESULTS = []  # list of NetboxResult
    # Init connection to Netbox via PyNetbox
    nb = Netbox.connect()
    # find the device instance in netbox
    dev = nb.dcim.devices.get(host.data["id"])
    # store params before changes
    before = get_changed_params(dev)

    dev.serial = napalm_facts.get("serial_number", "")
    dev.custom_fields["ni_update"] = True
    dev.custom_fields["ni_update_date"] = str(datetime.date.today())

    if dev.save():
        # store params after changes
        after = get_changed_params(dev)
        RESULTS.append(
            NetboxResultFactory.create_success(
                name=dev.name,
                action=Action.UPDATE,
                diff=get_diff(before, after),
                message=f"{dev.name} - Serial number updated: {dev.serial}",
            )
        )
    else:
        RESULTS.append(
            NetboxResultFactory.create_no_change(
                name=dev.name,
                action=Action.UPDATE,
                message=f"{dev.name} - Serial number already exists: {dev.serial}",
            )
        )
    return RESULTS


def get_changed_params(nb_device):
    return {
        "serial": nb_device.serial,
        "ni_update": nb_device.custom_fields["ni_update"],
        "ni_update_date": nb_device.custom_fields["ni_update_date"],
    }
