import re
from collections import defaultdict

from dictdiffer import diff
from netutils.interface import canonical_interface_name, canonical_interface_name_list
from netutils.vlan import vlanconfig_to_list

PYATS_PLATFORM_MAPPER = {
    'ios': "ios",
    'cisco_ios': "ios",
    'iosxr': "iosxr",
    'cisco_iosxr': "iosxr",
    'iosxe': 'iosxe',
    'cisco_iosxe': 'iosxe',
    'nxos': "nxos_ssh",
    'nxos_ssh': 'nxos_ssh',
    'junos': 'junos',
    'juniper': 'junos',
    'sros': 'sros',
    'nokia': 'sros'
}

BASE_INTERFACES_EXTENDED = {
    "TenGigE": "TenGigabitEthernet",
    "Ap": "AppGigabitEthernet"
}


def determine_pyats_platform(os):
    return PYATS_PLATFORM_MAPPER.get(os, os)


def is_interface_physical(name):  # pylint: disable=R0911
    """Function evaluate if an interface is likely to be a physical interface.
    Args:
      name (str): name of the interface to evaluate
    Return:
      True, False or None
    """
    # Match most physical interface Cisco that contains Ethernet
    #  GigabitEthernet0/0/2
    #  GigabitEthernet0/0/2:3
    #  TenGigabitEthernet0/0/4
    cisco_physical_intf = r"^[a-zA-Z]+[Ethernet][0-9\/\:]+$"

    # Match Sub interfaces finishing with ".<number>"
    sub_intf = r".*\.[0-9]+$"

    # Regex for loopback and vlan interface
    loopback = r"^(L|l)(oopback|o)[0-9]+$"
    vlan = r"^(V|v)(lan)[0-9]+$"

    # Generic physical interface match
    #  mainly looking for <int>/<int> or <int>/<int>/<int> at the end
    generic_physical_intf = r"^[a-zA-Z\-]+[0-9]+\/[0-9\/\:]+$"

    # Match Juniper Interfaces
    jnpr_physical_intf = r"^[a-z]+\-[0-9\/\:]+$"

    if re.match(loopback, name):
        return False
    if re.match(vlan, name):
        return False
    if re.match(cisco_physical_intf, name):
        return True
    if re.match(sub_intf, name):
        return False
    if re.match(jnpr_physical_intf, name):
        return True
    if re.match(generic_physical_intf, name):
        return True

    return None


def is_interface_lag(name):
    """Function to evaluate if an interface is likely to be a lag.
    Args:
      name (str): name of the interface to evaluate
    Return:
      True, False or None
    """
    port_channel_intf = r"^port\-channel[0-9]+$"
    po_intf = r"^po[0-9]+$"
    ae_intf = r"^ae[0-9]+$"
    bundle_intf = r"^Bundle\-Ether[0-9]+$"

    if re.match(port_channel_intf, name.lower()):
        return True
    if re.match(ae_intf, name):
        return True
    if re.match(po_intf, name):
        return True
    if re.match(bundle_intf, name):
        return True

    return None


def get_netbox_interface_type(ifc_name):
    is_physical = is_interface_physical(ifc_name)
    is_lag = is_interface_lag(ifc_name)

    if is_lag:
        return 'lag'
    elif is_physical is False:
        return 'virtual'
    else:
        return 'other'


def canonical_interface_name_edited(interface):
    return canonical_interface_name(interface, BASE_INTERFACES_EXTENDED)


def canonical_interface_name_list_edited(interfaces):
    return canonical_interface_name_list(interfaces, BASE_INTERFACES_EXTENDED)


def get_diff(before, after):
    diff_result = defaultdict(dict)
    changes = list(diff(before, after))
    for change in changes:
        type = change[0]
        name = change[1]
        diffs = change[2]

        if isinstance(name, list) and len(name) == 2:
            name = name[1]

        diff_result[type][name] = list(diffs)

    return dict(diff_result)


def get_address_from_netbox_task(task):
    return task.host.get("primary_ip", {}).get("address", "").split('/')[0]


def vlanconfig_to_list_edited(trunks_data):
    try:
        return vlanconfig_to_list(trunks_data)
    except ValueError as e:
        return []
    except Exception as e:
        raise e


def remove_key_from_results(results: dict, key="NOT_CHANGED"):
    results_without_not_changed_data = dict(results)
    # Remove NOT_CHANGED keys from results
    for device, tasks in results_without_not_changed_data.items():
        for task, output in tasks.items():
            if output.get("results", {}).get(key, None):
                output['results'].pop(key)

    return results_without_not_changed_data
